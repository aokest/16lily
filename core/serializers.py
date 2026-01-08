from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Opportunity, OpportunityLog, PerformanceTarget, Competition, MarketActivity, Customer, Contact, ActivityLog, CustomerTag, OpportunityTeamMember, ExternalIdMap, CustomerCohort, DepartmentModel, JobTitle
from .models import ApprovalRequest, SocialMediaStats, SocialMediaAccount, DailyReport

class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = DepartmentModel
        fields = ['id', 'name', 'parent', 'parent_name', 'manager', 'manager_name', 'category', 'category_display']
        
    def get_manager_name(self, obj):
        if not obj.manager: return ""
        name = f"{obj.manager.last_name}{obj.manager.first_name}".strip()
        return name if name else obj.manager.username
# from .models import SocialMediaAdmin, SocialMediaAccountChangeLog, SocialMediaAdminHistory
from .models import SubmissionLog
from .models import AIConfiguration

class CustomerSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    contacts = serializers.SerializerMethodField()
    tags_detail = serializers.SerializerMethodField()
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'owner']

    def get_owner_name(self, obj):
        if not obj.owner:
            return "Unknown"
        name = f"{obj.owner.last_name}{obj.owner.first_name}".strip()
        return name if name else obj.owner.username

    def get_contacts(self, obj):
        data = []
        for c in obj.contacts.all():
            data.append({'id': c.id, 'name': c.name, 'phone': c.phone, 'email': c.email})
        return data
    def get_tags_detail(self, obj):
        return [{'id': t.id, 'name': t.name, 'color': t.color} for t in obj.tags.all()]
    def create(self, validated_data):
        # 移除非模型字段
        tag_ids = validated_data.pop('tag_ids', [])
        obj = super().create(validated_data)
        if tag_ids:
            obj.tags.set(CustomerTag.objects.filter(id__in=tag_ids))
        return obj
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        obj = super().update(instance, validated_data)
        if tag_ids is not None:
            obj.tags.set(CustomerTag.objects.filter(id__in=tag_ids))
        return obj

class JobTitleSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    class Meta:
        model = JobTitle
        fields = ['id', 'name', 'category', 'category_display']

class UserProfileSerializer(serializers.ModelSerializer):
    department_display = serializers.SerializerMethodField()
    department_link = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentModel.objects.all(),
        required=False,
        allow_null=True
    )
    job_title = serializers.PrimaryKeyRelatedField(
        queryset=JobTitle.objects.all(),
        required=False,
        allow_null=True
    )
    job_category_display = serializers.CharField(source='get_job_category_display', read_only=True)
    job_rank_display = serializers.CharField(source='get_job_rank_display', read_only=True)
    job_rank_level_display = serializers.CharField(source='get_job_rank_level_display', read_only=True)
    full_position_display = serializers.CharField(source='get_full_position_display', read_only=True)
    department_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'department', 'department_link', 'department_display', 'report_to',
            'job_category', 'job_category_display', 
            'job_rank', 'job_rank_display',
            'job_rank_level', 'job_rank_level_display',
            'job_title', 'full_position_display',
            'job_position', 'job_level' # Deprecated but kept
        ]
        extra_kwargs = {
            'department': {'read_only': False},
        }

    def get_department_display(self, obj):
        return obj.get_department_display()

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'department', 'profile']

    def get_profile(self, obj):
        try:
            return UserProfileSerializer(obj.profile).data
        except Exception:
            return None

    def get_full_name(self, obj):
        name = f"{obj.last_name}{obj.first_name}".strip()
        return name if name else obj.username

    def get_department(self, obj):
        try:
            return obj.profile.get_department_display()
        except Exception:
            return ""

class UserManagementSerializer(serializers.ModelSerializer):
    """
    Serializer for User Management (CRUD)
    Handles password hashing and nested profile updates
    """
    profile = serializers.SerializerMethodField()
    profile_write = UserProfileSerializer(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    department = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'department', 'profile', 'profile_write']
        read_only_fields = ['date_joined']

    def get_profile(self, obj):
        try:
            return UserProfileSerializer(obj.profile).data
        except Exception:
            return None

    def get_department(self, obj):
        try:
            return obj.profile.get_department_display()
        except Exception:
            return ""

    def create(self, validated_data):
        profile_data = validated_data.pop('profile_write', {})
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        # Create or update profile
        if profile_data:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        else:
            # Ensure profile exists even if empty
            UserProfile.objects.get_or_create(user=user)
            
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile_write', {})
        password = validated_data.pop('password', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        
        # Update Profile
        if profile_data:
            UserProfile.objects.update_or_create(user=instance, defaults=profile_data)
            
        return instance

class OpportunityLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.SerializerMethodField()
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    opportunity_amount = serializers.DecimalField(source='opportunity.amount', max_digits=12, decimal_places=2, read_only=True)
    opportunity_status = serializers.CharField(source='opportunity.stage', read_only=True)
    
    class Meta:
        model = OpportunityLog
        fields = ['id', 'action', 'content', 'created_at', 'operator', 'operator_name', 'opportunity_name', 'opportunity_amount', 'opportunity_status']

    def get_operator_name(self, obj):
        if not obj.operator:
            return "Unknown"
        name = f"{obj.operator.last_name}{obj.operator.first_name}".strip()
        return name if name else obj.operator.username

class OpportunityTeamMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    class Meta:
        model = OpportunityTeamMember
        fields = '__all__'
        read_only_fields = ['created_at']
    def validate_role(self, value):
        mapping = {
            'MEMBER': 'OTHER',
            'SALES_REP': 'SALES',
            'PRE_SALES': 'PRE_SALES',
            'PRODUCT': 'PDM',
            'PM': 'PM'
        }
        return mapping.get(value, value)
    def get_user_name(self, obj):
        try:
            return obj.user.username if obj.user else obj.name
        except Exception:
            return obj.name
    def get_role_display(self, obj):
        try:
            return obj.get_role_display()
        except Exception:
            return ''

class ActivityLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.SerializerMethodField()
    operator_dept = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'type', 'type_display', 'action', 'content', 'created_at', 'actor', 'operator_name', 'operator_dept', 'department']

    def get_operator_name(self, obj):
        if not obj.actor:
            return "系统"
        name = f"{obj.actor.last_name}{obj.actor.first_name}".strip()
        return name if name else obj.actor.username

    def get_operator_dept(self, obj):
        # 优先使用冗余字段
        if obj.department:
            return obj.department
        # 兜底：从 actor profile 获取
        try:
            if obj.actor and hasattr(obj.actor, 'profile') and obj.actor.profile.department_link:
                return obj.actor.profile.department_link.name
            return getattr(obj.actor.profile, 'department', '')
        except Exception:
            return ''

class ApprovalRequestSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    model_key = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    object_summary = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = ['id', 'status', 'request_type', 'reason', 'created_at', 'updated_at', 'applicant', 'approver', 'applicant_name', 'approver_name', 'model_key', 'model_name', 'object_id', 'object_summary']
        read_only_fields = ['created_at', 'updated_at']

    def get_applicant_name(self, obj):
        if not obj.applicant: return '系统'
        name = f"{obj.applicant.last_name}{obj.applicant.first_name}".strip()
        if name: return name
        # Fallback for admin/managers
        if obj.applicant.username == 'admin': return '管理员'
        return obj.applicant.username

    def get_approver_name(self, obj):
        if not obj.approver: return '未分配'
        name = f"{obj.approver.last_name}{obj.approver.first_name}".strip()
        if name: return name
        if obj.approver.username == 'admin': return '管理员'
        return obj.approver.username

    def get_model_key(self, obj):
        if not obj.content_type: return 'unknown'
        return obj.content_type.model

    def get_model_name(self, obj):
        if not obj.content_type: return '未知'
        model = obj.content_type.model
        mapping = {
            'opportunity': '商机',
            'customer': '客户',
            'contact': '联系人',
            'marketactivity': '市场活动',
            'competition': '赛事信息',
            'socialmediastats': '社媒数据',
            'socialmediaaccount': '社媒账号',
            'announcement': '公告'
        }
        return mapping.get(model, model)

    def get_object_summary(self, obj):
        if not obj.content_object: return f"ID: {obj.object_id} (已删除)"
        # Try specific fields first
        if hasattr(obj.content_object, 'name'):
            return obj.content_object.name
        if hasattr(obj.content_object, 'title'):
            return obj.content_object.title
        # Fallback to str
        return str(obj.content_object)

class SocialMediaStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaStats
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'record_date', 'creator']

# class SocialMediaAdminSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SocialMediaAdmin
#         fields = ['user', 'admin_name', 'admin_account_name', 'admin_phone', 'assigned_at', 'revoked_at']

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    stats_recent = serializers.SerializerMethodField()
    account_username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    display_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = SocialMediaAccount
        fields = ['id', 'platform', 'account_name', 'account_id', 'manager', 'url', 'created_at', 'stats_recent', 'account_username', 'display_name']
        read_only_fields = ['created_at']

    def get_stats_recent(self, obj):
        qs = SocialMediaStats.objects.filter(account=obj).order_by('-date', '-created_at')[:10]
        return [
            {
                'id': s.id,
                'date': s.date,
                'fans_count': s.fans_count,
                'status': s.status
            } for s in qs
        ]
    
    def create(self, validated_data):
        # 映射别名到真实字段
        account_username = validated_data.pop('account_username', None)
        display_name = validated_data.pop('display_name', None)
        if account_username and not validated_data.get('account_name'):
            validated_data['account_name'] = account_username
        # 兼容中文平台名称
        platform = validated_data.get('platform')
        platform_map = {
            '抖音': 'DOUYIN',
            '公众号': 'WECHAT_OFFICIAL',
            '微博': 'WEIBO',
            '视频号': 'WECHAT_VIDEO',
            'B站': 'BILIBILI',
            '小红书': 'XIAOHONGSHU'
        }
        if platform and platform in platform_map:
            validated_data['platform'] = platform_map[platform]
        elif platform and platform not in [c[0] for c in SocialMediaAccount.Platform.choices]:
            validated_data['platform'] = 'OTHER'
        # display_name 暂不持久化，兼容前端字段
        # 唯一性校验：platform + account_name
        platform = validated_data.get('platform')
        account_name = validated_data.get('account_name')
        if platform and account_name:
            from .models import SocialMediaAccount
            if SocialMediaAccount.objects.filter(platform=platform, account_name=account_name).exists():
                raise serializers.ValidationError({'account_name': ['账号已存在于该平台']})
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        account_username = validated_data.pop('account_username', None)
        validated_data.pop('display_name', None)
        if account_username:
            validated_data['account_name'] = account_username
        platform = validated_data.get('platform')
        platform_map = {
            '抖音': 'DOUYIN',
            '公众号': 'WECHAT_OFFICIAL',
            '微博': 'WEIBO',
            '视频号': 'WECHAT_VIDEO',
            'B站': 'BILIBILI',
            '小红书': 'XIAOHONGSHU'
        }
        if platform and platform in platform_map:
            validated_data['platform'] = platform_map[platform]
        elif platform and platform not in [c[0] for c in SocialMediaAccount.Platform.choices]:
            validated_data['platform'] = 'OTHER'
        # 唯一性校验：platform + account_name
        platform = validated_data.get('platform', instance.platform)
        account_name = validated_data.get('account_name', instance.account_name)
        from .models import SocialMediaAccount
        if platform and account_name:
            exists = SocialMediaAccount.objects.filter(platform=platform, account_name=account_name).exclude(pk=instance.pk).exists()
            if exists:
                raise serializers.ValidationError({'account_name': ['账号已存在于该平台']})
        return super().update(instance, validated_data)

class OpportunitySerializer(serializers.ModelSerializer):
    logs = OpportunityLogSerializer(many=True, read_only=True)
    creator_name = serializers.SerializerMethodField()
    sales_manager_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    # 兼容前端新增字段（忽略持久化）
    expected_sign_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    win_rate = serializers.IntegerField(write_only=True, required=False)
    source = serializers.CharField(write_only=True, required=False, allow_blank=True)
    product_line = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_industry = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_region = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    project_manager_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_name_write = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['creator', 'created_at', 'updated_at', 'profit']
        extra_kwargs = {
            'sales_manager': {'required': False},
            'customer_company': {'required': False},
            'customer_contact_name': {'required': False},
        }
    
    def to_internal_value(self, data):
        # 将 customer_name 兼容为 customer_company
        if 'customer_name' in data and 'customer_company' not in data:
            data['customer_company'] = data.get('customer_name')
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        # 移除非模型字段
        for k in ['expected_sign_date','win_rate','source','product_line','customer_industry','customer_region','customer_phone','project_manager_name','ai_raw_text','customer_name_write','customer_name']:
            validated_data.pop(k, None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        for k in ['expected_sign_date','win_rate','source','product_line','customer_industry','customer_region','customer_phone','project_manager_name','ai_raw_text','customer_name_write','customer_name']:
            validated_data.pop(k, None)
        return super().update(instance, validated_data)

    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.name
        return obj.customer_company or "未关联客户"

    def get_creator_name(self, obj):
        if not obj.creator:
            return "系统"
        name = f"{obj.creator.last_name}{obj.creator.first_name}".strip()
        return name if name else obj.creator.username

    def get_sales_manager_name(self, obj):
        if not obj.sales_manager:
            return "未分配"
        name = f"{obj.sales_manager.last_name}{obj.sales_manager.first_name}".strip()
        return name if name else obj.sales_manager.username

class UserSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        name = f"{obj.last_name}{obj.first_name}".strip()
        return name if name else obj.username

class PerformanceTargetSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False, allow_null=True
    )
    target_type_display = serializers.CharField(source='get_target_type_display', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)

    class Meta:
        model = PerformanceTarget
        fields = [
            'id', 'target_type', 'target_type_display', 'period', 'period_display',
            'year', 'month', 'quarter', 'user', 'user_id', 'department', 'department_name',
            'target_contract_amount', 'target_gross_profit', 'target_revenue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else ''
        except Exception:
            return ''


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

class MarketActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketActivity
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at']
    def get_customer_name(self, obj):
        try:
            return obj.customer.name if obj.customer else ''
        except Exception:
            return ''

class CustomerTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTag
        fields = '__all__'

class ExternalIdMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalIdMap
        fields = '__all__'
        read_only_fields = ['created_at']

class CustomerCohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCohort
        fields = '__all__'
        read_only_fields = ['created_at', 'creator']

class SubmissionLogSerializer(serializers.ModelSerializer):
    """
    AI提交日志序列化，用于管理员查看与导出
    """
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = SubmissionLog
        fields = ['id','status','text_input','intent','entity','fields','filters','result_payload','user','user_name','created_at']
        read_only_fields = ['created_at']
    def get_user_name(self, obj):
        return obj.user.username if obj.user else ''

class AIConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConfiguration
        fields = ['id','name','provider','api_key','base_url','model_name','is_active','supports_vision','updated_at']
        read_only_fields = ['updated_at']

    def validate_provider(self, value):
        """
        将提供商代码统一转为大写，以匹配模型中的 Choice 定义
        """
        return value.upper()

from .models import Project, ProjectCard

class ProjectCardSerializer(serializers.ModelSerializer):
    assignees_detail = serializers.SerializerMethodField()
    class Meta:
        model = ProjectCard
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_assignees_detail(self, obj):
        return [{'id': u.id, 'name': f"{u.last_name}{u.first_name}".strip() or u.username} for u in obj.assignees.all()]

class ProjectSerializer(serializers.ModelSerializer):
    change_logs = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    opportunity_name = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    followup_rhythm_display = serializers.CharField(source='get_followup_rhythm_display', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'owner': {'required': False, 'allow_null': True},
            'customer': {'required': False, 'allow_null': True},
            'opportunity': {'required': False, 'allow_null': True},
        }
        
    def get_owner_name(self, obj):
        if not obj.owner: return "未分配"
        name = f"{obj.owner.last_name}{obj.owner.first_name}".strip()
        return name if name else obj.owner.username

    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else "未关联客户"

    def get_opportunity_name(self, obj):
        return obj.opportunity.name if obj.opportunity else "未关联商机"

    def get_progress(self, obj):
        """
        根据 auto_update_progress 决定返回自动计算的进度还是手动填写的进度
        """
        if not obj.auto_update_progress:
            return obj.progress_manual
            
        # 自动计算逻辑：基于卡片状态
        cards = obj.cards.all()
        if not cards.exists():
            return 0
        total = cards.count()
        done = cards.filter(status='DONE').count()
        return int((done / total) * 100)
    
    def get_change_logs(self, obj):
        from .models import ProjectChangeLog
        logs = ProjectChangeLog.objects.filter(project=obj).order_by('-created_at')[:20]
        return [{'field_name': l.field_name, 'old_value': l.old_value, 'new_value': l.new_value, 'action': l.action, 'content': l.content, 'operator': getattr(l.operator, 'username', ''), 'created_at': l.created_at} for l in logs]

class DailyReportSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    projects_detail = serializers.SerializerMethodField()
    mentions_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyReport
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']
        
    def get_user_name(self, obj):
        if not obj.user: return "系统"
        name = f"{obj.user.last_name}{obj.user.first_name}".strip()
        return name if name else obj.user.username
        
    def get_projects_detail(self, obj):
        return [{'id': p.id, 'name': p.name} for p in obj.projects.all()]

    def get_mentions_detail(self, obj):
        return [{'id': u.id, 'name': f"{u.last_name}{u.first_name}".strip() or u.username} for u in obj.mentions.all()]

from .models import Notification, Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['created_at', 'published_at', 'creator']

    def get_creator_name(self, obj):
        if not obj.creator:
            return "系统"
        name = f"{obj.creator.last_name}{obj.creator.first_name}".strip()
        return name if name else obj.creator.username

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']
        extra_kwargs = {
            'recipient': {'required': False}, # We handle multiple recipients in viewset
        }
        
    def get_sender_name(self, obj):
        # If it's a mention from a daily report, return the author
        if obj.type == Notification.Type.MENTION and obj.content_object and hasattr(obj.content_object, 'user'):
            user = obj.content_object.user
            name = f"{user.last_name}{user.first_name}".strip()
            return name if name else user.username
        if obj.type == Notification.Type.NORMAL:
            return '系统通知'
        if obj.content_object and hasattr(obj.content_object, 'applicant'):
             user = obj.content_object.applicant
             name = f"{user.last_name}{user.first_name}".strip()
             return name if name else user.username
        return '系统通知'
