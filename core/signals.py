from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from .models import (
    Opportunity, TodoTask, WorkReport, Competition, MarketActivity, Customer, Contact,
    DepartmentModel, Department, OpportunityLog, ApprovalStatus
)
from .models_transfer import OpportunityTransferApplication
from django.contrib.auth.models import User
from .services.ai_service import AIService
import datetime

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
    if instance.ai_raw_text and (is_new or is_placeholder):
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

@receiver(models.signals.post_save, sender=Opportunity)
def auto_create_opportunity_log(sender, instance, created, **kwargs):
    from .models import OpportunityLog
    if created:
        OpportunityLog.objects.create(
            opportunity=instance,
            operator=instance.creator if instance.creator else instance.sales_manager, # Fallback
            action="创建商机",
            content=f"创建了商机：{instance.name}，预计金额：{instance.amount}",
            stage_snapshot=instance.get_stage_display()
        )

@receiver(pre_save, sender=WorkReport)
def process_workreport_ai(sender, instance, **kwargs):
    if instance.ai_raw_input and not instance.content:
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
    
    if instance.ai_raw_text and (is_new or is_placeholder):
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
    
    if instance.ai_raw_text and (is_new or is_placeholder):
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
    
    if instance.ai_raw_text and (is_new or is_placeholder):
        data = get_ai_service().parse_customer(instance.ai_raw_text)
        if data:
            instance.name = data.get('name') or instance.name
            instance.industry = data.get('industry') or instance.industry
            instance.website = data.get('website') or instance.website
            instance.legal_representative = data.get('legal_representative') or instance.legal_representative
            
            if data.get('scale'):
                for choice in Customer.Scale.choices:
                    if choice[0] == data.get('scale'):
                        instance.scale = data.get('scale')
                        break

@receiver(pre_save, sender=Contact)
def process_contact_ai(sender, instance, **kwargs):
    is_new = instance.pk is None
    is_placeholder = instance.name in ['新联系人', 'New Contact', '联系人', '未命名']
    
    if instance.ai_raw_text and (is_new or is_placeholder):
        data = get_ai_service().parse_contact(instance.ai_raw_text)
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

@receiver(post_save, sender=OpportunityLog)
def process_opportunity_transfer(sender, instance, created, **kwargs):
    """
    处理商机移交逻辑：当创建了一条动作为'商机移交'的跟进记录时，自动发起移交审批流程
    """
    if created and instance.action == '商机移交' and instance.transfer_target:
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
        if hasattr(current_owner, 'profile') and current_owner.profile.reports_to:
            manager = current_owner.profile.reports_to.user
            
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
