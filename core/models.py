from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# --- System Configuration Models ---

class AIConfiguration(models.Model):
    """
    AI模型配置
    """
    class Provider(models.TextChoices):
        OPENAI = 'OPENAI', 'OpenAI (及兼容接口)'
        DEEPSEEK = 'DEEPSEEK', 'DeepSeek'
        OLLAMA = 'OLLAMA', 'Ollama (Local)'
        MOONSHOT = 'MOONSHOT', 'Kimi (Moonshot)'
        ALIYUN = 'ALIYUN', '通义千问'
        OTHER = 'OTHER', '其他'

    name = models.CharField(max_length=50, verbose_name='配置名称', help_text='例如：DeepSeek生产环境')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.DEEPSEEK, verbose_name='服务提供商')
    
    api_key = models.CharField(max_length=200, verbose_name='API Key')
    base_url = models.CharField(max_length=200, verbose_name='API Base URL', blank=True, help_text='如果是OpenAI兼容接口，请填写Base URL，例如：https://api.deepseek.com/v1')
    
    model_name = models.CharField(max_length=100, verbose_name='模型名称', default='deepseek-chat', help_text='例如：gpt-3.5-turbo, deepseek-chat, moonshot-v1-8k')
    
    is_active = models.BooleanField(default=False, verbose_name='设为默认', help_text='勾选此项，则在未选择模型时默认使用此配置')
    supports_vision = models.BooleanField(default=False, verbose_name='支持视觉/OCR', help_text='该模型是否支持图片识别功能')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, *args, **kwargs):
        # Ensure only one config is active
        if self.is_active:
            AIConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"

    class Meta:
        verbose_name = 'AI模型配置'
        verbose_name_plural = 'AI模型配置'


class PromptTemplate(models.Model):
    """
    独立提示词模板配置
    """
    class Scene(models.TextChoices):
        GLOBAL = 'GLOBAL', '全局系统提示词 (System)'
        OPPORTUNITY = 'OPPORTUNITY', '商机录入'
        CUSTOMER = 'CUSTOMER', '客户录入'
        COMPETITION = 'COMPETITION', '赛事信息'
        MARKET = 'MARKET', '市场活动'
        TODO = 'TODO', '待办任务'
        REPORT = 'REPORT', '工作报告'
        OTHER = 'OTHER', '其他'

    name = models.CharField(max_length=100, verbose_name='模板名称', help_text='例如：标准商机解析模板V1')
    scene = models.CharField(max_length=50, choices=Scene.choices, default=Scene.GLOBAL, verbose_name='应用场景')
    
    template = models.TextField(verbose_name='提示词内容', help_text='在此编写详细的提示词指令')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='同一场景建议只启用一个，系统将使用最新启用的模板')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, *args, **kwargs):
        # Optional: If we want to enforce single active per scene, we can do it here.
        # For now, we will just let the service pick the latest active one.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_scene_display()}] {self.name}"

    class Meta:
        verbose_name = '提示词模板'
        verbose_name_plural = '提示词模板'
        ordering = ['scene', '-updated_at']

# 新增：层级化部门模型
class DepartmentModel(models.Model):
    """
    组织架构部门模型（支持多级树状结构）
    """
    name = models.CharField(max_length=100, verbose_name='部门名称')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='上级部门')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments', verbose_name='部门负责人')
    
    # 部门性质分类
    class Category(models.TextChoices):
        SALES = 'SALES', '销售部门'
        RND = 'RND', '研发产线'
        POC = 'POC', 'POC/技术支持'
        LAB = 'LAB', '实验室'
        FUNCTIONAL = 'FUNCTIONAL', '职能部门' # HR, Finance, etc.
        OTHER = 'OTHER', '其他'
        
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, verbose_name='部门性质')
    
    description = models.TextField(blank=True, verbose_name='部门职责/描述')
    
    # 可视化/排序字段
    order = models.IntegerField(default=0, verbose_name='显示顺序')
    
    class Meta:
        verbose_name = '组织架构'
        verbose_name_plural = '组织架构'
        ordering = ['order', 'name']

    def __str__(self):
        # 显示层级路径，例如 "总经办 > 销售部 > 华北区"
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

# 部门定义 (保留 TextChoices 用于历史数据兼容，逐步迁移到 DepartmentModel)
class Department(models.TextChoices):
    SALES = 'SALES', '销售部'
    GAME = 'GAME', '春秋GAME'  # 原POC
    GROUP_MARKETING = 'GROUP_MARKETING', '集团市场部'
    LAB = 'LAB', '标准实践实验室'
    RND = 'RND', '研发中心'
    OTHER = 'OTHER', '其他'

# 细分角色/岗位定义
class JobRole(models.TextChoices):
    # 销售
    SALES_REP = 'SALES_REP', '销售经理'
    PRE_SALES = 'PRE_SALES', '售前工程师'
    
    # 春秋GAME (原POC)
    GAME_ENGINEER = 'GAME_ENGINEER', '春秋GAME工程师'
    
    # 集团市场部
    MARKETING_RND = 'MARKETING_RND', '市场部研发人员'
    
    # 研发中心细分
    PRODUCT = 'PRODUCT', '产品经理'
    TEST = 'TEST', '测试工程师'
    IMPL = 'IMPL', '实施工程师'
    FRONTEND = 'FRONTEND', '前端工程师'
    BACKEND = 'BACKEND', '后端工程师'
    UI = 'UI', 'UI设计师'
    
    # 实验室细分
    LAB_XIAORANG = 'LAB_XIAORANG', '霄壤实验室人员'
    LAB_GAMMA = 'LAB_GAMMA', '伽玛实验室人员'
    
    # 通用
    MEMBER = 'MEMBER', '普通成员'
    MANAGER = 'MANAGER', '部门经理'
    OTHER = 'OTHER', '其他人员'

class UserProfile(models.Model):
    """
    用户扩展信息，关联部门和角色
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='关联用户')
    
    # 旧部门字段 (保留兼容) - 已在前端隐藏
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.OTHER, verbose_name='所属部门(旧)', editable=False)
    
    # 新部门关联 (FK)
    department_link = models.ForeignKey(DepartmentModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name='所属部门')
    
    job_role = models.CharField(max_length=20, choices=JobRole.choices, default=JobRole.MEMBER, verbose_name='具体角色/岗位')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像URL')
    wechat_openid = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信OpenID')
    
    # 内部汇报关系
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name='汇报给')

    def __str__(self):
        dept = self.department_link.name if self.department_link else self.get_department_display()
        return f"{self.user.username} - {dept} - {self.get_job_role_display()}"

    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'

# --- Approval Workflow Models ---

class ApprovalStatus(models.TextChoices):
    DRAFT = 'DRAFT', '草稿'
    PENDING = 'PENDING', '待确认/审核中'
    APPROVED = 'APPROVED', '已确认/已发布'
    REJECTED = 'REJECTED', '已驳回'

class TodoTask(models.Model):
    """
    待办任务模型
    """
    class TaskType(models.TextChoices):
        APPROVAL = 'APPROVAL', '审批任务'
        NOTICE = 'NOTICE', '通知提醒'
        
    class SourceType(models.TextChoices):
        WORKFLOW = 'WORKFLOW', '流程审核' # 来源于系统流程自动生成
        MANUAL_SELF = 'MANUAL_SELF', '个人自建' # 用户自己创建
        MANUAL_ASSIGN = 'MANUAL_ASSIGN', '上级指派' # 管理员指派
        AI_GENERATED = 'AI_GENERATED', 'AI智能解析' # AI解析生成
        
    title = models.CharField(max_length=200, verbose_name='任务标题')
    description = models.TextField(blank=True, verbose_name='任务描述')
    
    # 来源类型
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.MANUAL_SELF, verbose_name='任务来源')
    
    # 指派给谁
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_tasks', verbose_name='负责人')
    
    # 截止时间 (AI解析常用)
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    
    # 关联的对象 (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    def __str__(self):
        return f"{self.title} - {self.assignee.username}"

    class Meta:
        verbose_name = '待办任务'
        verbose_name_plural = '待办任务'
        ordering = ['-created_at']

class Announcement(models.Model):
    """
    公告系统
    """
    class Type(models.TextChoices):
        SYSTEM = 'SYSTEM', '系统公告'
        DEPARTMENT = 'DEPARTMENT', '部门公告'
        
    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.DEPARTMENT, verbose_name='公告类型')
    
    target_departments = models.JSONField(default=list, blank=True, verbose_name='目标部门', help_text='选择接收公告的部门')
    
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_announcements', verbose_name='发布人')
    
    # 审批状态
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT, verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'

class WorkReport(models.Model):
    """
    个人工作报告 (日报/周报/月报)
    """
    class ReportType(models.TextChoices):
        DAILY = 'DAILY', '日报'
        WEEKLY = 'WEEKLY', '周报'
        MONTHLY = 'MONTHLY', '月报'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_reports', verbose_name='汇报人')
    type = models.CharField(max_length=20, choices=ReportType.choices, default=ReportType.DAILY, verbose_name='报告类型')
    
    report_date = models.DateField(verbose_name='汇报日期')
    content = models.TextField(verbose_name='工作内容', blank=True)
    
    # AI 辅助
    ai_raw_input = models.TextField(blank=True, verbose_name='AI原始指令', help_text='在此输入一句话总结，AI将自动生成详细报告内容。例如：“今天完成了商机A的拜访，和张总确认了需求，明天计划写方案”')
    ai_summary = models.TextField(blank=True, verbose_name='AI总结')
    
    # 关联项目 (多对多) - 可以关联商机、赛事、活动
    related_opportunities = models.ManyToManyField('Opportunity', blank=True, verbose_name='关联商机')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.report_date}"
    
    def save(self, *args, **kwargs):
        # Simple AI generation logic (Mock)
        if self.ai_raw_input and not self.content:
            # Mocking AI generation
            self.content = f"【AI自动生成报告】\n根据您的指令：{self.ai_raw_input}\n\n1. 今日重点工作：\n- 完成了相关客户拜访与需求确认。\n2. 详细进展：\n- {self.ai_raw_input}\n3. 明日计划：\n- 继续跟进后续事项。"
            self.ai_summary = f"已完成：{self.ai_raw_input} (AI摘要)"
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '工作报告'
        verbose_name_plural = '工作报告'

class SocialMediaStats(models.Model):
    """
    社交媒体粉丝统计
    """
    platform = models.CharField(max_length=100, verbose_name='平台/账号名称', help_text='如：永信至诚公众号, 勒索病毒头条, i春秋, 春秋伽玛')
    fans_count = models.IntegerField(default=0, verbose_name='粉丝数')
    record_date = models.DateField(auto_now_add=True, verbose_name='记录日期')
    
    class Meta:
        verbose_name = '粉丝数据统计'
        verbose_name_plural = '粉丝数据统计'

# --- CRM Core Models ---

class Customer(models.Model):
    """
    客户企业/组织
    """
    class Scale(models.TextChoices):
        SMALL = 'SMALL', '小微企业 (<50人)'
        MEDIUM = 'MEDIUM', '中型企业 (50-500人)'
        LARGE = 'LARGE', '大型企业 (500-2000人)'
        ENTERPRISE = 'ENTERPRISE', '集团/超大型 (>2000人)'
        GOV = 'GOV', '政府机构/事业单位'

    class Status(models.TextChoices):
        POTENTIAL = 'POTENTIAL', '潜在客户'
        ACTIVE = 'ACTIVE', '活跃客户'
        KEY = 'KEY', '重点客户'
        CHURNED = 'CHURNED', '流失客户'

    name = models.CharField(max_length=200, unique=True, verbose_name='客户名称')
    industry = models.CharField(max_length=100, blank=True, verbose_name='所属行业')
    scale = models.CharField(max_length=20, choices=Scale.choices, blank=True, verbose_name='规模')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.POTENTIAL, verbose_name='客户状态')
    
    # 丰富化字段
    legal_representative = models.CharField(max_length=100, blank=True, verbose_name='法人代表')
    registered_capital = models.CharField(max_length=100, blank=True, verbose_name='注册资金')
    address = models.CharField(max_length=255, blank=True, verbose_name='办公地址')
    website = models.URLField(blank=True, verbose_name='官网')
    
    # AI 预备字段
    ai_raw_text = models.TextField(blank=True, verbose_name='原始信息(AI解析)', help_text='在此粘贴大段客户介绍，后续通过AI自动提取')
    
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_customers', verbose_name='负责销售')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户管理'
        verbose_name_plural = '客户管理'
        ordering = ['-created_at']

class Contact(models.Model):
    """
    客户联系人
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts', verbose_name='所属客户')
    name = models.CharField(max_length=100, verbose_name='姓名')
    title = models.CharField(max_length=100, blank=True, verbose_name='职位/头衔')
    
    phone = models.CharField(max_length=50, blank=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    wechat = models.CharField(max_length=100, blank=True, verbose_name='微信号')
    
    department = models.CharField(max_length=100, blank=True, verbose_name='所在部门')
    is_decision_maker = models.BooleanField(default=False, verbose_name='是否关键决策人')
    
    # 汇报关系 (用于绘制客户组织架构)
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name='汇报给')
    
    # AI 预备字段
    ai_raw_text = models.TextField(blank=True, verbose_name='原始信息(AI解析)')
    
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.name} - {self.customer.name}"

    class Meta:
        verbose_name = '联系人'
        verbose_name_plural = '联系人'

# --- Competition & Activity Models ---

class Competition(models.Model):
    """
    赛事管理 (春秋GAME主导)
    """
    name = models.CharField(max_length=200, verbose_name='比赛名称')
    time = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateField(verbose_name='结束时间', null=True, blank=True)
    location = models.CharField(max_length=200, verbose_name='活动地点', blank=True)
    
    # New Fields from Excel
    project_name = models.CharField(max_length=200, verbose_name='立项名称/实训项目名称', blank=True)
    project_code = models.CharField(max_length=100, verbose_name='项目编号', blank=True)
    type = models.CharField(max_length=50, verbose_name='类型', help_text='比赛/实战/培训/集训/其他', blank=True)
    
    contact_person = models.CharField(max_length=50, verbose_name='对接人', blank=True)
    owner_name = models.CharField(max_length=50, verbose_name='负责人', blank=True) # Text for Excel import compatibility
    department_name = models.CharField(max_length=100, verbose_name='部门', blank=True)
    
    duration = models.CharField(max_length=50, verbose_name='比赛时长', blank=True)
    team_count = models.CharField(max_length=50, verbose_name='队伍数量', blank=True)
    leader_count = models.CharField(max_length=50, verbose_name='领队人数', blank=True)
    participant_count = models.CharField(max_length=50, verbose_name='实际总人数', blank=True)
    
    challenge_count = models.CharField(max_length=50, verbose_name='题目数量', blank=True)
    challenge_type = models.CharField(max_length=100, verbose_name='题目类型', blank=True)
    
    impact_level = models.CharField(max_length=50, verbose_name='赛事/影响力热度', blank=True)
    host_type = models.CharField(max_length=50, verbose_name='主办类型', blank=True)
    organizers = models.TextField(verbose_name='组织机构', blank=True)
    
    # Existing Fields
    class Format(models.TextChoices):
        ONLINE = 'ONLINE', '线上'
        OFFLINE = 'OFFLINE', '线下'
        HYBRID = 'HYBRID', '线上+线下'
    
    format = models.CharField(max_length=20, choices=Format.choices, default=Format.OFFLINE, verbose_name='举办形式')
    
    system_format = models.CharField(max_length=100, blank=True, verbose_name='赛制', help_text='如：CTF, AWD, 攻防演练等')
    scale = models.CharField(max_length=100, blank=True, verbose_name='参赛人数/规模 (旧)')
    target_audience = models.CharField(max_length=200, blank=True, verbose_name='面向对象')
    industry = models.CharField(max_length=100, blank=True, verbose_name='所属行业')
    level = models.CharField(max_length=50, blank=True, verbose_name='级别')
    
    description = models.TextField(blank=True, verbose_name='备注/赛事详情')
    ai_raw_text = models.TextField(blank=True, verbose_name='原始信息(AI解析)')

    # 确认人：春秋GAME
    confirmed_by = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'profile__department': Department.GAME}, related_name='confirmed_competitions', null=True, blank=True, verbose_name='确认人(春秋GAME)')
    
    # 审批状态 (Mapping Excel '状态': 已完成 -> APPROVED, etc.)
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT, verbose_name='状态')
    
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_competitions', verbose_name='录入人', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '赛事信息'
        verbose_name_plural = '赛事信息'

class MarketActivity(models.Model):
    """
    市场活动 (集团市场部主导)
    """
    name = models.CharField(max_length=200, verbose_name='活动名称')
    time = models.DateField(verbose_name='活动时间')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    
    type = models.CharField(max_length=100, verbose_name='活动类型', help_text='如：展会, 沙龙, 峰会等')
    scale = models.CharField(max_length=100, blank=True, verbose_name='规模')
    
    description = models.TextField(blank=True, verbose_name='活动详情')
    ai_raw_text = models.TextField(blank=True, verbose_name='原始信息(AI解析)')

    # 确认人：集团市场部
    confirmed_by = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'profile__department': Department.GROUP_MARKETING}, related_name='confirmed_activities', null=True, blank=True, verbose_name='确认人(集团市场部)')
    
    # 审批状态
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT, verbose_name='审批状态')

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_activities', verbose_name='录入人')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '市场活动'
        verbose_name_plural = '市场活动'

class Opportunity(models.Model):
    """
    商机模型
    """
    class Stage(models.TextChoices):
        CONTACT = 'CONTACT', '接触阶段'
        REQ_ANALYSIS = 'REQ_ANALYSIS', '需求分析'
        INITIATION = 'INITIATION', '客户立项'
        BIDDING = 'BIDDING', '招采阶段'
        DELIVERY = 'DELIVERY', '交付实施'
        AFTER_SALES = 'AFTER_SALES', '售后阶段'
        COMPLETED = 'COMPLETED', '项目完成'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', '进行中'
        WON = 'WON', '赢单'
        LOST = 'LOST', '输单'
        SUSPENDED = 'SUSPENDED', '挂起'
        COMPLETED = 'COMPLETED', '已完成'

    name = models.CharField(max_length=200, verbose_name='商机名称')
    
    # 客户关联 (新)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='opportunities', null=True, blank=True, verbose_name='关联客户')
    
    # 客户信息 (保留文本字段以兼容历史数据，新建时优先使用关联客户)
    customer_name = models.CharField(max_length=100, verbose_name='客户姓名(文本)')
    customer_company = models.CharField(max_length=200, verbose_name='客户公司(文本)')
    customer_org = models.CharField(max_length=200, blank=True, null=True, verbose_name='客户组织/部门')
    
    # 状态与阶段
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.CONTACT, verbose_name='当前阶段')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name='商机状态')
    
    # 审批状态 (商机也可以有确认流程)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT, verbose_name='审批状态')
    
    # 财务数据
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='预计金额', help_text='项目预计签约的总金额（商机池金额）')
    signed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='新签合同金额', help_text='实际签订合同的金额')
    
    # 毛利 (Contract Profit)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='毛利', help_text='合同金额 - 预计成本')
    
    # 回款毛利 (Gross Profit / Return Profit)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='回款毛利', help_text='扣除成本后的实际回款毛利')
    
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='确认收入金额', help_text='财务确认的收入金额')
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    expected_sign_date = models.DateField(null=True, blank=True, verbose_name='预计签约时间')
    
    # 人员关联
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_opportunities', verbose_name='登记人')
    sales_manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_opportunities', verbose_name='负责销售')
    
    # 团队成员 (多对多) - 保留用于简单关联，详细信息使用 OpportunityTeamMember
    team_members = models.ManyToManyField(User, related_name='participated_opportunities', blank=True, verbose_name='参与团队成员(简单)')

    # 丰富化字段 (Enrichment)
    description = models.TextField(blank=True, verbose_name='商机描述/备注', help_text='商机背景、需求详情等')
    win_rate = models.IntegerField(default=0, verbose_name='赢单概率(%)', help_text='0-100之间')
    competitors = models.CharField(max_length=255, blank=True, verbose_name='竞争对手', help_text='多个对手用逗号分隔')
    source = models.CharField(max_length=100, blank=True, verbose_name='商机来源', help_text='如：老客户推荐, 市场活动, 招标公告等')
    
    # User requested fields
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name='项目经理')
    product_line = models.CharField(max_length=100, blank=True, verbose_name='所属产线', help_text='例如：网络靶场, 城市安全, 培训服务等')
    customer_industry = models.CharField(max_length=100, blank=True, verbose_name='客户行业', help_text='例如：教育, 金融, 能源, 政府等')
    customer_region = models.CharField(max_length=100, blank=True, verbose_name='客户区域', help_text='例如：华北区, 北京, 广东等')
    customer_contact_name = models.CharField(max_length=100, blank=True, verbose_name='客户联系人', help_text='关键联系人姓名')

    # AI 预备字段
    ai_raw_text = models.TextField(blank=True, verbose_name='原始信息(AI解析)', help_text='在此粘贴大段商机介绍，后续通过AI自动提取')

    # 确认机制
    is_confirmed_by_sales = models.BooleanField(default=False, verbose_name='销售已确认生效')

    def save(self, *args, **kwargs):
        """
        重写保存方法：
        1. 如果确认收入为空，默认填充为新签合同金额
        2. 自动将负责销售添加到项目组成员中
        3. 如果选择了Customer，自动填充customer_company文本字段(如为空)
        """
        # 1. Auto-fill revenue
        if self.signed_amount and not self.revenue:
            self.revenue = self.signed_amount

        # 3. Auto-fill company name from Customer relation
        if self.customer and not self.customer_company:
            self.customer_company = self.customer.name
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 2. Auto-create Team Member for Sales Manager
        if self.sales_manager:
            try:
                if not self.detailed_members.filter(user=self.sales_manager).exists():
                    from django.apps import apps
                    TeamMember = apps.get_model('core', 'OpportunityTeamMember')
                    
                    TeamMember.objects.create(
                        opportunity=self,
                        user=self.sales_manager,
                        name=self.sales_manager.username,
                        role=JobRole.SALES_REP,
                        responsibility='负责销售(自动添加)',
                        start_date=self.created_at.date() if self.created_at else None
                    )
            except Exception as e:
                print(f"Auto-create team member failed: {e}")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商机'
        verbose_name_plural = '商机列表'
        ordering = ['-created_at']

class OpportunityTeamMember(models.Model):
    """
    商机项目组成员详情
    """
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='detailed_members', verbose_name='关联商机')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='系统用户')
    
    # 如果是外部人员或未注册人员，可填写名称
    name = models.CharField(max_length=100, blank=True, verbose_name='成员姓名(如非系统用户)')
    
    role = models.CharField(max_length=20, choices=JobRole.choices, default=JobRole.MEMBER, verbose_name='项目中角色')
    responsibility = models.TextField(blank=True, verbose_name='责任分工')
    
    workload = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, verbose_name='投入工时(人天)')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='进入项目时间')
    end_date = models.DateField(null=True, blank=True, verbose_name='离开项目时间')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='添加时间')

    def save(self, *args, **kwargs):
        if self.user and not self.name:
            self.name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.opportunity.name} - {self.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = '项目组成员'
        verbose_name_plural = '项目组成员'

class OpportunityLog(models.Model):
    """
    商机跟进记录/时间轴
    """
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='logs', verbose_name='关联商机')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    action = models.CharField(max_length=50, verbose_name='动作')
    content = models.TextField(verbose_name='跟进内容/备注')
    stage_snapshot = models.CharField(max_length=20, blank=True, null=True, verbose_name='当时阶段')
    
    # 新增：关联移交申请 (当action为'商机移交'时使用)
    transfer_target = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_logs', verbose_name='移交给谁')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    def __str__(self):
        return f"{self.opportunity.name} - {self.action} - {self.created_at}"

    class Meta:
        verbose_name = '跟进记录'
        verbose_name_plural = '跟进记录'


class PerformanceTarget(models.Model):
    """
    业绩目标模型
    """
    class Quarter(models.IntegerChoices):
        Q1 = 1, '第一季度'
        Q2 = 2, '第二季度'
        Q3 = 3, '第三季度'
        Q4 = 4, '第四季度'
        FULL_YEAR = 0, '全年'

    year = models.IntegerField(verbose_name='年份', default=2025)
    quarter = models.IntegerField(choices=Quarter.choices, default=Quarter.FULL_YEAR, verbose_name='季度 (0代表全年)')
    
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.SALES, verbose_name='目标部门')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='目标个人 (留空则为部门目标)')
    
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='新签合同金额目标', help_text='对应新签合同金额')
    # target_profit removed as requested
    target_gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='回款毛利目标', help_text='对应回款毛利')
    target_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='确认收入目标', help_text='对应确认收入金额')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        scope = self.user.username if self.user else self.get_department_display()
        period = f"{self.year}年" + (f" Q{self.quarter}" if self.quarter != 0 else " 全年")
        return f"{scope} - {period} 目标"

    class Meta:
        verbose_name = '业绩目标'
        verbose_name_plural = '业绩目标'
        unique_together = ['year', 'quarter', 'department', 'user']

# --- Import new models ---
from .models_transfer import OpportunityTransferApplication
