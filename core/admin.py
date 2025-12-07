from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.db.models import Sum
import csv
import re
import json
from datetime import datetime
from .models import (
    UserProfile, Opportunity, OpportunityLog, PerformanceTarget, OpportunityTeamMember, 
    Customer, Contact, Competition, MarketActivity, Announcement, TodoTask, WorkReport, SocialMediaStats, ApprovalStatus,
    DepartmentModel, AIConfiguration, PromptTemplate
)

# --- Common Export Action ---
@admin.action(description='导出选中数据为CSV')
def export_as_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name}.csv'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    
    # Get field names
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write header
    writer.writerow([field.verbose_name for field in fields])
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name)
            if hasattr(value, 'strftime'):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(value, '__call__'):
                value = value()
            row.append(str(value))
        writer.writerow(row)
    return response

# --- Workflow & Activity Actions ---

@admin.action(description='批准立项 (仅销售/管理员)')
def approve_opportunity(modeladmin, request, queryset):
    user = request.user
    is_sales = False
    if hasattr(user, 'profile'):
        dept = user.profile.department_link
        if dept and dept.category == DepartmentModel.Category.SALES:
            is_sales = True
        elif user.profile.department == 'SALES':
            is_sales = True
    
    if not (user.is_superuser or is_sales):
        modeladmin.message_user(request, "权限不足：仅【销售部门】人员或系统管理员可审批商机立项。", level='ERROR')
        return

    rows_updated = queryset.update(approval_status=ApprovalStatus.APPROVED)
    modeladmin.message_user(request, f"已批准 {rows_updated} 个商机立项。")

@admin.action(description='批准赛事 (仅春秋GAME)')
def approve_competition(modeladmin, request, queryset):
    user = request.user
    is_game = False
    if hasattr(user, 'profile'):
        dept = user.profile.department_link
        if dept and ('GAME' in dept.name or '春秋' in dept.name): 
             is_game = True
        elif user.profile.department == 'GAME':
             is_game = True
    
    if not (user.is_superuser or is_game):
        modeladmin.message_user(request, "权限不足：仅【春秋GAME】部门人员或系统管理员可审批赛事。", level='ERROR')
        return

    rows_updated = queryset.update(status=ApprovalStatus.APPROVED)
    modeladmin.message_user(request, f"已批准 {rows_updated} 个赛事。")

@admin.action(description='批准活动 (仅集团市场部)')
def approve_activity(modeladmin, request, queryset):
    user = request.user
    is_marketing = False
    if hasattr(user, 'profile'):
        dept = user.profile.department_link
        if dept and ('市场' in dept.name or 'Marketing' in dept.name): 
             is_marketing = True
        elif user.profile.department == 'GROUP_MARKETING':
             is_marketing = True
    
    if not (user.is_superuser or is_marketing):
        modeladmin.message_user(request, "权限不足：仅【集团市场部】人员或系统管理员可审批市场活动。", level='ERROR')
        return

    rows_updated = queryset.update(status=ApprovalStatus.APPROVED)
    modeladmin.message_user(request, f"已批准 {rows_updated} 个市场活动。")

@admin.action(description='批准/发布公告')
def approve_announcement(modeladmin, request, queryset):
    if not (request.user.is_superuser or request.user.has_perm('core.change_announcement')):
        modeladmin.message_user(request, "权限不足。", level='ERROR')
        return
    queryset.update(status=ApprovalStatus.APPROVED)
    modeladmin.message_user(request, "公告已发布。")


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'scene', 'is_active', 'updated_at')
    list_filter = ('scene', 'is_active')
    search_fields = ('name', 'template')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'scene', 'is_active')
        }),
        ('提示词内容', {
            'fields': ('template',),
            'description': '请在此输入详细的系统提示词。'
        }),
    )

@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'model_name', 'is_active', 'updated_at')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'model_name')
    list_editable = ('is_active',)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # Remove the problematic self._inject_ai_context(extra_context)
        # as AIConfigurationAdmin does not inherit from AIEnabledAdminMixin
        
        # Inject a connection test URL for the template to use
        extra_context['test_connection_url'] = 'test-connection/'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/change/test-connection/', self.admin_site.admin_view(self.test_connection_view), name='aiconfiguration-test-connection'),
        ]
        return custom_urls + urls

    def test_connection_view(self, request, object_id):
        from django.http import JsonResponse
        try:
            config = AIConfiguration.objects.get(pk=object_id)
            # Import AIService locally to avoid circular import issues
            from core.services.ai_service import AIService
            
            # Manually construct a service with this config
            service = AIService(config_id=config.id)
            
            # Try a simple "Hello" call
            result = service._call_llm_json("You are a connection tester.", "Reply with JSON: {'status': 'ok'}")
            
            if result and not result.get('error'):
                return JsonResponse({'status': 'success', 'message': '连接成功！API返回正常。', 'data': result})
            else:
                error_msg = result.get('error') if result else "Unknown error"
                return JsonResponse({'status': 'error', 'message': f'连接失败: {error_msg}'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@admin.register(DepartmentModel)
class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'parent', 'manager', 'order')
    list_filter = ('category', 'parent')
    search_fields = ('name',)
    ordering = ('order', 'name')
    autocomplete_fields = ['parent', 'manager']

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('org-chart/', self.admin_site.admin_view(self.org_chart_view), name='departmentmodel-org-chart'),
        ]
        return custom_urls + urls

    def org_chart_view(self, request):
        from django.shortcuts import render
        from .models import DepartmentModel
        import json
        
        def build_tree(dept):
            node = {
                'name': dept.name,
                'manager': dept.manager.username if dept.manager else "",
                'children': []
            }
            children = dept.children.all().order_by('order')
            for child in children:
                node['children'].append(build_tree(child))
            return node
            
        roots = DepartmentModel.objects.filter(parent__isnull=True).order_by('order')
        
        if roots.count() > 1:
            chart_data = {
                'name': '石榴粒粒 (总部)',
                'children': [build_tree(root) for root in roots]
            }
        elif roots.count() == 1:
            chart_data = build_tree(roots.first())
        else:
            chart_data = {'name': '暂无部门数据'}
            
        context = dict(
           self.admin_site.each_context(request),
           chart_data=json.dumps(chart_data),
           opts=self.model._meta,
        )
        return render(request, 'admin/core/departmentmodel/org_chart.html', context)


# --- User Admin ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户扩展信息'
    fk_name = 'user'
    fieldsets = (
        (None, {'fields': ('department_link', 'job_role', 'reports_to')}),
        ('其他信息', {'fields': ('avatar', 'wechat_openid')}),
    )

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_name', 'get_department_new', 'get_job_role', 'is_staff')
    actions = [export_as_csv]

    def get_name(self, instance):
        return f"{instance.last_name}{instance.first_name}"
    get_name.short_description = '姓名'

    def get_department_new(self, instance):
        if instance.profile.department_link:
            return instance.profile.department_link.name
        return instance.profile.get_department_display()
    get_department_new.short_description = '部门'

    def get_job_role(self, instance):
        return instance.profile.get_job_role_display()
    get_job_role.short_description = '角色'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class OpportunityLogInline(admin.TabularInline):
    model = OpportunityLog
    extra = 1

class OpportunityTeamMemberInline(admin.TabularInline):
    model = OpportunityTeamMember
    extra = 1
    fields = ('user', 'name', 'role', 'responsibility', 'workload', 'start_date', 'end_date')

class OpportunityForm(forms.ModelForm):
    expected_sign_date = forms.CharField(
        required=False, 
        label='预计签约时间', 
        help_text='支持格式: 2025-01-01, 20250101, 2025年1月1日',
        widget=forms.TextInput(attrs={'class': 'vDateField', 'placeholder': 'YYYY-MM-DD or natural text'})
    )

    def _parse_fuzzy_date(self, value):
        if not value: return None
        if isinstance(value, datetime) or hasattr(value, 'isoformat'): return value
        value = str(value).strip()
        try: return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError: pass
        if re.match(r'^\d{8}$', value): return datetime.strptime(value, '%Y%m%d').date()
        match = re.match(r'^(\d{2})年(\d{4})$', value)
        if match: return datetime.strptime(f"20{match.group(1)}{match.group(2)}", '%Y%m%d').date()
        match = re.match(r'^(\d{4})年(\d{1,2})月(\d{1,2})[日号]?$', value)
        if match: return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3))).date()
        return value

    def clean_expected_sign_date(self):
        value = self.cleaned_data.get('expected_sign_date')
        if not value: return None
        parsed = self._parse_fuzzy_date(value)
        if isinstance(parsed, str): 
             raise ValidationError("无法识别的日期格式，请使用 2025-01-01 或 20250101")
        return parsed

    class Meta:
        model = Opportunity
        fields = '__all__'
        exclude = ('ai_raw_text',)

class AIEnabledAdminMixin:
    """
    Mixin to inject AI configurations into change_form context
    """
    change_form_template = 'admin/core/ai_change_form.html'
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        self._inject_ai_context(extra_context)
        return super().add_view(request, form_url, extra_context=extra_context)
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        self._inject_ai_context(extra_context)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
        
    def _inject_ai_context(self, context):
        # Get all available AI configurations (active or not, but let's show all to allow selection)
        # Actually, usually we only show active ones or allow switching.
        # The user asked to select model.
        configs = AIConfiguration.objects.all().values('id', 'name', 'model_name', 'is_active')
        context['ai_configs'] = list(configs)
        context['ai_configs_json'] = json.dumps(list(configs))

@admin.register(Opportunity)
class OpportunityAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    form = OpportunityForm
    list_display = ('name', 'customer_company', 'get_sales_manager_name', 'stage_display', 'status_display', 'approval_status', 'amount', 'is_confirmed_by_sales')
    list_filter = ('stage', 'status', 'approval_status', 'sales_manager', 'is_confirmed_by_sales', 'customer')
    search_fields = ('name', 'customer_name', 'customer_company', 'customer__name')
    inlines = [OpportunityTeamMemberInline, OpportunityLogInline]
    filter_horizontal = ('team_members',)
    autocomplete_fields = ['customer']
    actions = [approve_opportunity, export_as_csv]

    def get_sales_manager_name(self, obj):
        if obj.sales_manager:
            full_name = f"{obj.sales_manager.last_name}{obj.sales_manager.first_name}"
            return full_name if full_name.strip() else obj.sales_manager.username
        return "-"
    get_sales_manager_name.short_description = '负责销售'
    get_sales_manager_name.admin_order_field = 'sales_manager__first_name'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            obj = self.get_queryset(request).get(pk=object_id)
            next_obj = self.get_queryset(request).filter(created_at__gt=obj.created_at).order_by('created_at').first()
            prev_obj = self.get_queryset(request).filter(created_at__lt=obj.created_at).order_by('-created_at').first()
            if next_obj: extra_context['next_url'] = f"../{next_obj.pk}/change/"
            if prev_obj: extra_context['prev_url'] = f"../{prev_obj.pk}/change/"
        except: pass
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    class Media:
        css = {'all': ('admin/css/custom_tooltips.css',)}
        js = ('admin/js/custom_tooltips.js', 'admin/js/admin_dynamic.js')

    def status_display(self, obj):
        colors = {'ACTIVE': 'blue', 'WON': 'green', 'LOST': 'red', 'SUSPENDED': 'orange', 'COMPLETED': 'purple'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">● {}</span>', color, obj.get_status_display())
    status_display.short_description = '状态'

    def stage_display(self, obj):
        return format_html('<span style="padding: 3px 8px; background-color: #f0f0f0; border-radius: 4px;">{}</span>', obj.get_stage_display())
    stage_display.short_description = '阶段'

@admin.action(description='导出选中的跟进记录')
def export_logs_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="opportunity_logs.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(['商机名称', '操作人', '动作', '内容', '阶段快照', '时间'])
    for log in queryset:
        writer.writerow([
            log.opportunity.name,
            log.operator.username,
            log.action,
            log.content,
            log.stage_snapshot or '',
            log.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response

@admin.register(OpportunityLog)
class OpportunityLogAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'get_operator_name', 'action', 'created_at')
    list_filter = ('action',)
    actions = [export_logs_csv]

    def get_operator_name(self, obj):
        if obj.operator:
            return f"{obj.operator.last_name}{obj.operator.first_name}" or obj.operator.username
        return "-"
    get_operator_name.short_description = '操作人'

@admin.register(PerformanceTarget)
class PerformanceTargetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year', 'quarter', 'department', 'user', 'target_amount')
    list_filter = ('year', 'quarter', 'department')
    search_fields = ('user__username',)

# --- CRM Admins ---
class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ('name', 'title', 'phone', 'email', 'wechat', 'is_decision_maker')

class OpportunityInline(admin.TabularInline):
    model = Opportunity
    extra = 0
    fields = ('name', 'stage', 'status', 'signed_amount', 'revenue', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

@admin.register(Customer)
class CustomerAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'industry', 'scale', 'status', 'get_owner_name', 'total_signed_amount', 'total_opportunities')
    list_filter = ('status', 'industry', 'scale', 'owner')
    search_fields = ('name', 'address')
    inlines = [ContactInline, OpportunityInline]
    actions = [export_as_csv]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser: return qs
        if hasattr(user, 'profile') and user.profile.job_role in ['MANAGER', 'DIRECTOR']: return qs
        return qs.filter(owner=user)

    def get_owner_name(self, obj):
        if obj.owner:
            return f"{obj.owner.last_name}{obj.owner.first_name}" or obj.owner.username
        return "-"
    get_owner_name.short_description = '负责销售'
    
    def total_signed_amount(self, obj):
        total = obj.opportunities.aggregate(sum=Sum('signed_amount'))['sum'] or 0
        return f"¥{total:,.2f}"
    total_signed_amount.short_description = '累计新签金额'
    
    def total_opportunities(self, obj):
        return obj.opportunities.count()
    total_opportunities.short_description = '商机数'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'title', 'phone', 'is_decision_maker')
    list_filter = ('customer', 'is_decision_maker')
    search_fields = ('name', 'customer__name', 'phone')
    actions = [export_as_csv]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser: return qs
        if hasattr(user, 'profile') and user.profile.job_role in ['MANAGER', 'DIRECTOR']: return qs
        return qs.filter(customer__owner=user)

@admin.register(Competition)
class CompetitionAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'status', 'time', 'location', 'type', 'project_name', 'owner_name', 'department_name')
    list_filter = ('status', 'format', 'industry', 'type')
    search_fields = ('name', 'location', 'project_name', 'owner_name')
    actions = [approve_competition, export_as_csv]
    
    fieldsets = (
        ('基础信息', {'fields': ('name', 'status', 'time', 'end_time', 'location', 'type')}),
        ('立项与组织', {'fields': ('project_name', 'project_code', 'contact_person', 'owner_name', 'department_name', 'organizers', 'host_type')}),
        ('赛事规模与详情', {'fields': ('duration', 'team_count', 'leader_count', 'participant_count', 'challenge_count', 'challenge_type', 'impact_level')}),
        ('其他属性 (旧字段)', {'fields': ('format', 'system_format', 'scale', 'target_audience', 'industry', 'level', 'description', 'ai_raw_text'), 'classes': ('collapse',)}),
        ('系统信息', {'fields': ('creator', 'confirmed_by'), 'classes': ('collapse',)})
    )
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='competition-import-excel'),
            path('kanban/', self.admin_site.admin_view(self.kanban_view), name='competition-kanban'),
        ]
        return custom_urls + urls

    def kanban_view(self, request):
        from django.shortcuts import render
        stages = ApprovalStatus.choices
        kanban_data = {}
        for stage_code, stage_label in stages:
            kanban_data[stage_label] = Competition.objects.filter(status=stage_code).order_by('-created_at')
        return render(request, 'admin/core/competition/kanban.html', {'kanban_data': kanban_data, 'title': '赛事看板'})

    def import_excel_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        if request.method == 'POST':
            messages.info(request, "Excel导入功能暂未恢复")
            return redirect('..')
        return render(request, 'admin/core/competition/import_excel.html')

@admin.register(MarketActivity)
class MarketActivityAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'status', 'time', 'location', 'type')
    list_filter = ('status', 'type')
    search_fields = ('name', 'location')
    actions = [approve_activity, export_as_csv]
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [path('kanban/', self.admin_site.admin_view(self.kanban_view), name='marketactivity-kanban')]
        return custom_urls + urls

    def kanban_view(self, request):
        from django.shortcuts import render
        stages = ApprovalStatus.choices
        kanban_data = {}
        for stage_code, stage_label in stages:
            kanban_data[stage_label] = MarketActivity.objects.filter(status=stage_code).order_by('-created_at')
        return render(request, 'admin/core/marketactivity/kanban.html', {'kanban_data': kanban_data, 'title': '市场活动看板'})

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creator', 'status', 'published_at')
    list_filter = ('type', 'status')
    search_fields = ('title', 'content')
    actions = [approve_announcement]

@admin.register(TodoTask)
class TodoTaskAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'assignee', 'deadline', 'is_completed', 'source_type')
    list_filter = ('is_completed', 'source_type', 'assignee')
    search_fields = ('title', 'description')

@admin.register(WorkReport)
class WorkReportAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'type', 'report_date', 'created_at')
    list_filter = ('type', 'report_date', 'user')
    search_fields = ('content',)

@admin.register(SocialMediaStats)
class SocialMediaStatsAdmin(admin.ModelAdmin):
    list_display = ('platform', 'fans_count', 'record_date')
    list_filter = ('platform', 'record_date')
