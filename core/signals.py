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
    pass # 移动到 post_save 处理，因为需要 instance.pk

@receiver(post_save, sender=Opportunity)
def auto_create_opportunity_log(sender, instance, created, **kwargs):
    from .models import OpportunityLog, ActivityLog
    if created:
        operator = getattr(instance, 'creator', None) or getattr(instance, 'sales_manager', None)
        OpportunityLog.objects.create(
            opportunity=instance,
            operator=operator,
            action="创建商机",
            content=f"创建了商机：{instance.name}，预计金额：{instance.amount}"
        )
    
    # 统一动态日志
    try:
        operator = getattr(instance, 'creator', None) or getattr(instance, 'sales_manager', None)
        dept_name = ""
        if operator and hasattr(operator, 'profile') and operator.profile.department_link:
            dept_name = operator.profile.department_link.name
            
        ActivityLog.objects.create(
            type=ActivityLog.Type.OPPORTUNITY,
            action="创建" if created else "更新",
            content=f"{instance.name} (预计金额: {instance.amount})",
            actor=operator,
            department=dept_name,
            content_type=ContentType.objects.get_for_model(Opportunity),
            object_id=instance.id
        )
    except Exception:
        pass

@receiver(post_save, sender=Project)
def log_project_activity(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        operator = instance.owner
        dept_name = ""
        if operator and hasattr(operator, 'profile') and operator.profile.department_link:
            dept_name = operator.profile.department_link.name

        ActivityLog.objects.create(
            type=ActivityLog.Type.PROJECT,
            action="创建" if created else "更新",
            content=f"项目: {instance.name} ({instance.code})",
            actor=operator,
            department=dept_name,
            content_type=ContentType.objects.get_for_model(Project),
            object_id=instance.id
        )
    except Exception:
        pass

@receiver(post_save, sender=DailyReport)
def log_daily_report_activity(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        operator = instance.user
        dept_name = ""
        if operator and hasattr(operator, 'profile') and operator.profile.department_link:
            dept_name = operator.profile.department_link.name

        ActivityLog.objects.create(
            type=ActivityLog.Type.DAILY_REPORT,
            action="创建" if created else "更新",
            content=f"日报: {instance.date}",
            actor=operator,
            department=dept_name,
            content_type=ContentType.objects.get_for_model(DailyReport),
            object_id=instance.id
        )
    except Exception:
        pass

@receiver(post_delete, sender=Opportunity)
@receiver(post_delete, sender=Customer)
@receiver(post_delete, sender=Contact)
@receiver(post_delete, sender=Project)
def log_deletion_activity(sender, instance, **kwargs):
    try:
        from .models import ActivityLog
        # 尝试从 instance 中获取最后的操作人，如果没记录则为空
        # 注意：post_delete 时 instance 已经从数据库移除，但对象属性还在内存中
        actor = getattr(instance, 'owner', None) or getattr(instance, 'creator', None) or getattr(instance, 'sales_manager', None) or getattr(instance, 'user', None)
        
        dept_name = ""
        if actor and hasattr(actor, 'profile') and actor.profile.department_link:
            dept_name = actor.profile.department_link.name

        model_name = sender._meta.verbose_name
        ActivityLog.objects.create(
            type=ActivityLog.Type.SYSTEM,
            action="删除",
            content=f"删除了{model_name}: {getattr(instance, 'name', str(instance))}",
            actor=actor,
            department=dept_name
        )
    except Exception:
        pass

    # if created and instance.approval_status == ApprovalStatus.PENDING:
    #     approver = find_department_manager(instance.sales_manager)
    #     create_approval(instance.creator or instance.sales_manager, approver, instance)

@receiver(pre_save, sender=WorkReport)
def process_workreport_ai(sender, instance, **kwargs):
    if getattr(instance, 'ai_raw_input', None) and not instance.content:
        data = get_ai_service().parse_work_report(instance.ai_raw_input)
        if data:
            instance.content = data.get('content') or instance.content
            instance.ai_summary = data.get('ai_summary') or instance.ai_summary
            if data.get('report_type'):
                for choice in WorkReport.ReportType.choices:
                    if choice[0] == data.get('report_type'):
                        instance.type = data.get('report_type')
                        break

@receiver(pre_save, sender=Competition)
def process_competition_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新赛事', 'New Competition', '赛事', '未命名']
    
    if getattr(instance, 'ai_raw_text', None) and (is_new or is_placeholder):
        data = get_ai_service().parse_competition(instance.ai_raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            if data.get('time'):
                instance.time = safe_parse_date(data.get('time'))
            instance.location = data.get('location') or instance.location
            instance.type = data.get('type') or instance.type
            instance.owner_name = data.get('owner_name') or instance.owner_name

@receiver(pre_save, sender=MarketActivity)
def process_activity_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新活动', 'New Activity', '活动', '未命名']
    
    if getattr(instance, 'ai_raw_text', None) and (is_new or is_placeholder):
        data = get_ai_service().parse_market_activity(instance.ai_raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            if data.get('time'):
                instance.time = safe_parse_date(data.get('time'))
            instance.location = data.get('location') or instance.location
            instance.type = data.get('type') or instance.type

@receiver(pre_save, sender=Customer)
def process_customer_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新客户', 'New Customer', '客户', '未命名']
    
    raw_text = getattr(instance, 'ai_raw_text', None)
    if raw_text and (is_new or is_placeholder):
        data = get_ai_service().parse_customer(raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            instance.industry = data.get('industry') or instance.industry
            instance.website = data.get('website') or instance.website
            # Note: legal_representative and scale are not in the current model

@receiver(post_save, sender=Customer)
def log_customer_created(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.CUSTOMER,
            action="创建客户" if created else "更新客户",
            content=instance.name,
            actor=instance.owner,
            content_type=ContentType.objects.get_for_model(Customer),
            object_id=instance.id
        )
    except Exception:
        pass

    # status is not on Customer model in current version
    # if created and hasattr(instance, 'status') and instance.status in ['PENDING', 'POTENTIAL']:
    #     approver = find_department_manager(instance.owner)
    #     create_approval(instance.owner, approver, instance)

@receiver(pre_save, sender=Contact)
def process_contact_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新联系人', 'New Contact', '联系人', '未命名']
    
    raw_text = getattr(instance, 'ai_raw_text', None)
    
    if raw_text and (is_new or is_placeholder):
        data = get_ai_service().parse_contact(raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            instance.title = data.get('title') or instance.title
            instance.phone = data.get('phone') or instance.phone
            instance.email = data.get('email') or instance.email
            
            # Try to link Customer if not set
            if not instance.customer_id and data.get('customer_name'):
                cust = Customer.objects.filter(name__icontains=data.get('customer_name')).first()
                if cust:
                    instance.customer = cust

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

@receiver(post_save, sender=Competition)
def log_competition_created(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.COMPETITION,
            action="创建赛事" if created else "更新赛事",
            content=instance.name,
            actor=getattr(instance, 'creator', None),
            content_type=ContentType.objects.get_for_model(Competition),
            object_id=instance.id
        )
    except Exception:
        pass
    
    # Competition doesn't have status in this version
    # if created and hasattr(instance, 'status') and instance.status == ApprovalStatus.PENDING:
    #     approver = User.objects.filter(profile__department=Department.GAME).filter(is_superuser=True).first() or find_department_manager(instance.creator)
    #     create_approval(instance.creator, approver, instance)

@receiver(post_save, sender=MarketActivity)
def log_activity_created(sender, instance, created, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.ACTIVITY,
            action="创建活动" if created else "更新活动",
            content=instance.name,
            actor=getattr(instance, 'owner', None), # owner instead of creator
            content_type=ContentType.objects.get_for_model(MarketActivity),
            object_id=instance.id
        )
    except Exception:
        pass
    # if created and instance.status == ApprovalStatus.PENDING:
    #     approver = User.objects.filter(profile__department=Department.GROUP_MARKETING).filter(is_superuser=True).first() or find_department_manager(instance.creator)
    #     create_approval(instance.creator, approver, instance)

@receiver(post_save, sender=OpportunityLog)
def process_opportunity_transfer(sender, instance, created, **kwargs):
    """
    处理商机移交逻辑：当创建了一条动作为'商机移交'的跟进记录时，自动发起移交审批流程
    """
    if created and instance.action == '商机移交' and getattr(instance, 'transfer_target', None):
        # 1. 创建移交申请
        application = OpportunityTransferApplication.objects.create(
            opportunity=instance.opportunity,
            applicant=instance.operator,
            current_owner=instance.opportunity.sales_manager,
            target_owner=instance.transfer_target,
            reason=instance.content or "通过跟进记录发起的移交",
            status=ApprovalStatus.PENDING
        )
        
        # 2. 查找审批人 (直属上级 > 超级管理员)
        manager = None
        current_owner = instance.opportunity.sales_manager
        
        # 尝试获取直属上级
        if hasattr(current_owner, 'profile') and current_owner.profile.report_to:
            manager = current_owner.profile.report_to
            
        # 兜底：超级管理员
        if not manager:
            manager = User.objects.filter(is_superuser=True).first()
            
        # 3. 创建待办事项
        if manager:
            TodoTask.objects.create(
                title=f"商机移交审批: {instance.opportunity.name}",
                description=f"来源: 跟进记录\n申请人: {instance.operator.username}\n目标负责人: {instance.transfer_target.username}\n原因: {application.reason}",
                source_type=TodoTask.SourceType.WORKFLOW,
                assignee=manager,
                content_object=application
            )
            create_approval(instance.operator, manager, application)
        # Receiver approval
        TodoTask.objects.create(
            title=f"确认接收商机: {instance.opportunity.name}",
            description=f"请确认接收该商机并与销售经理协同后续工作。",
            source_type=TodoTask.SourceType.WORKFLOW,
            assignee=instance.transfer_target,
            content_object=application
        )
        create_approval(instance.operator, instance.transfer_target, application)
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.OPPORTUNITY,
            action=instance.action,
            content=instance.content,
            actor=instance.operator,
            content_type=ContentType.objects.get_for_model(Opportunity),
            object_id=instance.opportunity_id
        )
    except Exception:
        pass

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        dept_name = ""
        if hasattr(user, 'profile') and user.profile.department_link:
            dept_name = user.profile.department_link.name

        ActivityLog.objects.create(
            type=ActivityLog.Type.USER,
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
        dept_name = ""
        if user and hasattr(user, 'profile') and user.profile.department_link:
            dept_name = user.profile.department_link.name

        ActivityLog.objects.create(
            type=ActivityLog.Type.USER,
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

from django.contrib.auth.signals import user_logged_in, user_logged_out

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type='ACTIVITY', # Use string to avoid circular import issues if Enum not ready
            action='用户登录',
            content=f"用户 {user.username} 登录系统",
            actor=user
        )
    except Exception:
        pass

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            type='ACTIVITY',
            action='用户登出',
            content=f"用户 {user.username} 登出系统",
            actor=user
        )
    except Exception:
        pass
