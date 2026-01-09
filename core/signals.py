from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from .models import (
    Opportunity, TodoTask, WorkReport, Competition, MarketActivity, Customer, Contact, SocialMediaStats,
    DepartmentModel, OpportunityLog, SocialMediaAccount, ApprovalRequest, 
    ApprovalStatus, Project, DailyReport, ActivityLog
)
from django.db.models.signals import pre_save, post_save, post_delete
from .models_transfer import OpportunityTransferApplication
from django.contrib.auth.models import User
from .services.ai_service import AIService
import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.signals import user_logged_in, user_logged_out

def get_ai_service():
    return AIService()

def safe_parse_date(date_str):
    if not date_str: return None
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def safe_parse_datetime(date_str):
    if not date_str: return None
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        try:
            # Fallback to date only
            d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return d
        except:
            return None

@receiver(pre_save, sender=TodoTask)
def process_todotask_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    should_trigger = instance.source_type == 'AI_GENERATED'
    
    if not should_trigger and is_new and instance.description and len(instance.description) > 10 and (not instance.title or len(instance.title) < 5):
        should_trigger = True
        
    if should_trigger:
        raw_text = instance.description
        data = get_ai_service().parse_todo_task(raw_text)
        if data:
            instance.title = data.get('title') or instance.title
            if data.get('description'):
                instance.description = data.get('description')
            
            if data.get('deadline'):
                parsed_dt = safe_parse_datetime(data.get('deadline'))
                if parsed_dt:
                    instance.deadline = parsed_dt
            
            if data.get('assignee'):
                instance.assignee = data.get('assignee')
            
            instance.source_type = 'AI_GENERATED'

@receiver(pre_save, sender=Opportunity)
def process_opportunity_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新商机', 'New Opportunity', '商机', '未命名']
    
    # 1. AI 解析逻辑
    # Optimization: Only run AI if the name is a placeholder. 
    # If the user has already filled in the name (e.g. via Frontend Form), skip this slow step.
    if getattr(instance, 'ai_raw_text', None) and is_placeholder:
        data = get_ai_service().parse_opportunity(instance.ai_raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            if data.get('amount'):
                instance.amount = data.get('amount')
            if data.get('customer_name'):
                instance.customer_company = data.get('customer_name')
                cust = Customer.objects.filter(name__icontains=data.get('customer_name')).first()
                if cust:
                    instance.customer = cust
            
            if data.get('sales_manager'):
                instance.sales_manager = data.get('sales_manager')
            
            if data.get('expected_sign_date'):
                instance.expected_sign_date = safe_parse_date(data.get('expected_sign_date'))
                
            if data.get('stage'):
                for choice in Opportunity.Stage.choices:
                    if choice[0] == data.get('stage'):
                        instance.stage = data.get('stage')
                        break
    
    # 2. 自动创建跟进记录 (OpportunityLog) 用于大屏展示
    # 注意：这里我们只在创建时自动生成一条“创建”日志。
    # 后续的更新，如果通过 Admin 编辑，通常 Admin 不会自动创建 Log，除非我们手动 override save_model
    # 但为了确保大屏有数据，我们在 created 时强制生成一条。

@receiver(post_save, sender=Opportunity)
def log_opportunity_created(sender, instance, created, **kwargs):
    if created:
        try:
            OpportunityLog.objects.create(
                opportunity=instance,
                operator=instance.creator,
                action='创建商机',
                content=f"创建新商机：{instance.name}"
            )
            
            # 同时也记录到 ActivityLog
            ActivityLog.objects.create(
                type=ActivityLog.Type.OPPORTUNITY,
                action="创建商机",
                content=f"{instance.name}-{instance.customer_company}",
                actor=instance.creator,
                content_type=ContentType.objects.get_for_model(Opportunity),
                object_id=instance.id
            )
        except Exception:
            pass
    else:
        # Check if stage changed? (Optional: if needed)
        pass

@receiver(post_save, sender=Contact)
def log_contact_created(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        customer_name = instance.customer.name if instance.customer else "个人"
        # 尝试获取负责人，默认为 None
        actor = getattr(instance, 'owner', None)
        ActivityLog.objects.create(
            type=ActivityLog.Type.CONTACT,
            action="创建联系人" if created else "更新联系人",
            content=f"{instance.name}-{customer_name}",
            actor=actor,
            content_type=ContentType.objects.get_for_model(Contact),
            object_id=instance.id
        )
    except Exception:
        pass

@receiver(post_save, sender=Project)
def log_project_created(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.PROJECT,
            action="创建项目" if created else "更新项目",
            content=f"{instance.name}",
            actor=instance.manager,
            content_type=ContentType.objects.get_for_model(Project),
            object_id=instance.id
        )
    except Exception:
        pass

@receiver(post_save, sender=DailyReport)
def log_daily_report_created(sender, instance, created, **kwargs):
    if created:
        try:
            from .models import ActivityLog
            ActivityLog.objects.create(
                type=ActivityLog.Type.ACTIVITY,
                action="提交日报",
                content=f"{instance.date} 日报",
                actor=instance.user,
                content_type=ContentType.objects.get_for_model(DailyReport),
                object_id=instance.id
            )
        except Exception:
            pass

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        # 尝试获取用户部门
        dept_name = ""
        if hasattr(user, 'profile'):
            dept_name = user.profile.get_department_display()
            
        ActivityLog.objects.create(
            type=ActivityLog.Type.ACTIVITY,
            action="登录",
            content=f"用户 {user.username} 登录系统",
            actor=user,
            department=dept_name
        )
    except Exception:
        pass

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        # 尝试获取用户部门
        dept_name = ""
        if hasattr(user, 'profile'):
            dept_name = user.profile.get_department_display()

        ActivityLog.objects.create(
            type=ActivityLog.Type.ACTIVITY,
            action="登出",
            content=f"用户 {user.username if user else '未知'} 登出系统",
            actor=user,
            department=dept_name
        )
    except Exception:
        pass

def find_department_manager(user: User):
    if hasattr(user, 'profile') and user.profile.department_link:
        dept = user.profile.department_link
        if dept.manager:
            return dept.manager
    # Fallback: chain via report_to
    if hasattr(user, 'profile') and user.profile.report_to:
        return user.profile.report_to
    # Fallback: superuser
    return User.objects.filter(is_superuser=True).first()

def create_approval(applicant: User, approver: User, obj):
    if not approver:
        approver = User.objects.filter(is_superuser=True).first()
    return ApprovalRequest.objects.create(
        applicant=applicant,
        approver=approver,
        status=ApprovalStatus.PENDING,
        content_type=ContentType.objects.get_for_model(obj.__class__),
        object_id=obj.pk
    )

@receiver(post_save, sender=SocialMediaStats)
def log_social_stats(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        platform = instance.account.platform if instance.account else "未知"
        ActivityLog.objects.create(
            type=ActivityLog.Type.ACTIVITY,
            action="维护粉丝" if not created else "创建粉丝记录",
            content=f"{platform}-{instance.fans_count}",
            actor=instance.creator,
            content_type=ContentType.objects.get_for_model(SocialMediaStats),
            object_id=instance.id
        )
    except Exception:
        pass
    # 粉丝数据无需审批：不再创建审批请求

@receiver(models.signals.post_save, sender=ApprovalRequest)
def process_approval_result(sender, instance, created, **kwargs):
    """
    当审批状态变为 APPROVED 时，执行后续逻辑
    """
    if not created and instance.status == ApprovalStatus.APPROVED:
        # 1. 如果是商机移交申请
        if instance.content_type.model == 'opportunitytransferapplication':
            try:
                app = instance.content_object
                if app and app.status == ApprovalStatus.PENDING:
                    app.status = ApprovalStatus.APPROVED
                    app.approved_at = datetime.datetime.now()
                    app.save()
                    
                    # 执行移交
                    opp = app.opportunity
                    opp.sales_manager = app.target_owner
                    opp.save()
                    
                    # Log
                    OpportunityLog.objects.create(
                        opportunity=opp,
                        operator=instance.approver or app.applicant,
                        action='商机移交完成',
                        content=f"商机已从 {app.current_owner} 移交给 {app.target_owner}"
                    )
            except Exception:
                pass

@receiver(pre_save, sender=Customer)
def generate_customer_code(sender, instance, **kwargs):
    """
    自动生成客户编号: CUST-{YYYYMM}-{SEQ}
    例如: CUST-202310-001
    """
    if not instance.customer_code:
        now = datetime.datetime.now()
        prefix = f"CUST-{now.strftime('%Y%m')}"
        
        # 查找当月最大的编号
        # 注意：简单实现，高并发下可能有冲突，但对于内部CRM系统足够
        last_cust = Customer.objects.filter(customer_code__startswith=prefix).order_by('-customer_code').first()
        
        if last_cust and last_cust.customer_code:
            try:
                # 提取序号部分
                last_seq = int(last_cust.customer_code.split('-')[-1])
                new_seq = last_seq + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
            
        instance.customer_code = f"{prefix}-{new_seq:03d}"
