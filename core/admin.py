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
    Customer, Contact, Competition, MarketActivity, Announcement, TodoTask, SocialMediaStats,
    DepartmentModel, AIConfiguration, PromptTemplate, SocialMediaAccount, CustomerTag, ExternalIdMap, CustomerCohort, SubmissionLog,
    Project, ProjectCard, ProjectChangeLog, DailyReport, ApprovalRequest, ApprovalStatus, SystemRelease
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

@admin.action(description='批准/发布公告')
def approve_announcement(modeladmin, request, queryset):
    if not (request.user.is_superuser or request.user.has_perm('core.change_announcement')):
        modeladmin.message_user(request, "权限不足。", level='ERROR')
        return
    queryset.update(status=Announcement.Status.APPROVED)
    modeladmin.message_user(request, "公告已发布。")

# --- AI Context Mixin ---
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
        configs = AIConfiguration.objects.all().values('id', 'name', 'model_name', 'is_active')
        context['ai_configs'] = list(configs)
        context['ai_configs_json'] = json.dumps(list(configs))


# --- Model Admins ---

@admin.register(SystemRelease)
class SystemReleaseAdmin(admin.ModelAdmin):
    list_display = ('version', 'title', 'release_date', 'status', 'is_current')
    list_filter = ('status', 'is_current')
    search_fields = ('version', 'title', 'content')
    ordering = ('-release_date',)

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
        from .models import AIConfiguration
        from .services.ai_service import AIService
        try:
            config = AIConfiguration.objects.get(pk=object_id)
            service = AIService(config_id=config.id)
            # Simple test call
            msg = service._call_llm("Hi", "Test connection")
            return JsonResponse({'status': 'success', 'message': f'Connection successful. Response: {msg[:50]}...'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'region', 'owner', 'created_at')
    list_filter = ('industry', 'region')
    search_fields = ('name', 'industry')
    actions = [export_as_csv]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser: return qs
        # Simple permission logic
        return qs

@admin.register(Opportunity)
class OpportunityAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'customer', 'amount', 'stage', 'sales_manager', 'created_at')
    list_filter = ('stage', 'created_at')
    search_fields = ('name', 'customer__name')
    actions = [export_as_csv]

@admin.register(Competition)
class CompetitionAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'time', 'location', 'type', 'owner_name')
    list_filter = ('type', 'start_date')
    search_fields = ('name', 'location')

@admin.register(MarketActivity)
class MarketActivityAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'time', 'location', 'type')
    list_filter = ('type', 'date')
    search_fields = ('name', 'location')

@admin.register(TodoTask)
class TodoTaskAdmin(AIEnabledAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_completed', 'deadline', 'user')
    list_filter = ('priority', 'is_completed')
    search_fields = ('title',)

@admin.register(PerformanceTarget)
class PerformanceTargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_type', 'target_contract_amount', 'year', 'period')
    list_filter = ('target_type', 'year')
    search_fields = ('user__username',)

@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ('platform', 'account_name', 'manager', 'fans_count_display')
    list_filter = ('platform',)
    search_fields = ('account_name',)
    
    def fans_count_display(self, obj):
        latest = obj.stats.order_by('-date').first()
        return latest.fans_count if latest else '-'
    fans_count_display.short_description = '最新粉丝数'

@admin.register(SocialMediaStats)
class SocialMediaStatsAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'fans_count', 'read_count', 'interaction_count')
    list_filter = ('date', 'account__platform')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'department', 'job_title')
    search_fields = ('user__username', 'phone')

@admin.register(DepartmentModel)
class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'parent')

@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('request_type', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'request_type')
    actions = ['approve_requests', 'reject_requests']
    
    @admin.action(description='批量通过')
    def approve_requests(self, request, queryset):
        queryset.update(status=ApprovalStatus.APPROVED)
        
    @admin.action(description='批量驳回')
    def reject_requests(self, request, queryset):
        queryset.update(status=ApprovalStatus.REJECTED)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    actions = [approve_announcement]

# Register other models simply
admin.site.register(Contact)
admin.site.register(OpportunityLog)
admin.site.register(OpportunityTeamMember)
admin.site.register(CustomerTag)
admin.site.register(ExternalIdMap)
admin.site.register(CustomerCohort)
admin.site.register(SubmissionLog)
admin.site.register(Project)
admin.site.register(ProjectCard)
admin.site.register(ProjectChangeLog)
admin.site.register(DailyReport)
