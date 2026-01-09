from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# --- System Enums ---

class ApprovalStatus(models.TextChoices):
    PENDING = 'PENDING', '待审批'
    APPROVED = 'APPROVED', '已通过'
    REJECTED = 'REJECTED', '已拒绝'
    DRAFT = 'DRAFT', '草稿'

# --- System Configuration Models ---

class AIConfiguration(models.Model):
    """
    AI模型配置
    """
    class Provider(models.TextChoices):
        OPENAI = 'OPENAI', 'OpenAI (及兼容接口)'
        DEEPSEEK = 'DEEPSEEK', 'DeepSeek'
        GEMINI = 'GEMINI', 'Google Gemini'
        OLLAMA = 'OLLAMA', 'Ollama (Local)'
        MOONSHOT = 'MOONSHOT', 'Kimi (Moonshot)'
        ALIYUN = 'ALIYUN', '通义千问'
        GLM = 'GLM', '智谱GLM (OpenAPI兼容)'
        OTHER = 'OTHER', '其他'

    name = models.CharField(max_length=50, verbose_name='配置名称', help_text='例如：DeepSeek生产环境')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.DEEPSEEK, verbose_name='服务提供商')
    
    # User ownership (Null means system-wide config)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_configs', verbose_name='所属用户')
    
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
        MANAGEMENT = 'MANAGEMENT', '管理'
        POC = 'POC', 'POC'
        RND = 'RND', '研发'
        LAB = 'LAB', '实验室'
        FUNCTION = 'FUNCTION', '职能'
        SALES = 'SALES', '销售'
    
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FUNCTION, verbose_name='部门性质')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'

class Notification(models.Model):
    """
    系统通知
    """
    class Type(models.TextChoices):
        SYSTEM = 'SYSTEM', '系统通知'
        NORMAL = 'NORMAL', '普通消息'
        MENTION = 'MENTION', '提及通知'
        APPROVAL = 'APPROVAL', '审批通知'
        TASK = 'TASK', '任务提醒'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收人')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM, verbose_name='类型')
    
    # Generic relation to source object (e.g. DailyReport, ApprovalRequest)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    class Meta:
        verbose_name = '系统通知'
        verbose_name_plural = '系统通知'
        ordering = ['-created_at']

# --- CRM Core Models ---

class Customer(models.Model):
    """
    客户模型
    """
    name = models.CharField(max_length=100, verbose_name='客户名称')
    customer_code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='客户编号', help_text='例如：CUST-001')
    industry = models.CharField(max_length=50, blank=True, verbose_name='所属行业')
    scale = models.CharField(max_length=20, blank=True, verbose_name='规模', help_text='SMALL/MEDIUM/LARGE')
    status = models.CharField(max_length=20, default='POTENTIAL', verbose_name='状态', help_text='POTENTIAL/ACTIVE/LOST')
    region = models.CharField(max_length=50, blank=True, verbose_name='所属区域', help_text='例如：华北、华东、海外')
    address = models.CharField(max_length=200, blank=True, verbose_name='地址')
    website = models.URLField(blank=True, verbose_name='官网')
    legal_representative = models.CharField(max_length=50, blank=True, verbose_name='法人代表')
    description = models.TextField(blank=True, verbose_name='备注')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='customers', verbose_name='负责人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户列表'
        ordering = ['-created_at']

class CustomerTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色', help_text='可填#RRGGBB或预设色名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    customers = models.ManyToManyField(Customer, related_name='tags', blank=True, verbose_name='关联客户')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户标签'
        verbose_name_plural = '客户标签'

class Contact(models.Model):
    """
    联系人模型
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts', verbose_name='所属客户')
    name = models.CharField(max_length=50, verbose_name='姓名')
    title = models.CharField(max_length=50, blank=True, verbose_name='职务')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    is_primary = models.BooleanField(default=False, verbose_name='是否主要联系人')
    
    # New fields for relationship map
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name='汇报给')
    decision_role = models.CharField(max_length=50, blank=True, verbose_name='决策角色', help_text='例如：决策者、影响者、使用者、把关人')
    attitude = models.CharField(max_length=50, blank=True, verbose_name='态度', help_text='例如：支持、中立、反对')
    
    # AI Analysis Raw Text
    ai_raw_text = models.TextField(blank=True, verbose_name='AI分析原始文本')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.name} ({self.customer.name})"

    class Meta:
        verbose_name = '联系人'
        verbose_name_plural = '联系人列表'

class Opportunity(models.Model):
    """
    商机模型
    """
    class Stage(models.TextChoices):
        CONTACT = 'CONTACT', '接触阶段 (10%)'
        REQ_ANALYSIS = 'REQ_ANALYSIS', '需求分析 (30%)'
        INITIATION = 'INITIATION', '客户立项 (50%)'
        BIDDING = 'BIDDING', '招采阶段 (70%)'
        SIGNED = 'SIGNED', '已签约 (90%)'
        DELIVERY = 'DELIVERY', '交付实施 (95%)'
        AFTER_SALES = 'AFTER_SALES', '售后阶段 (100%)'
        COMPLETED = 'COMPLETED', '项目完成 (100%)'
        SUSPENDED = 'SUSPENDED', '商机暂停 (0%)'
        TERMINATED = 'TERMINATED', '商机终止 (0%)'
        WON = 'WON', '赢单 (100%)'
        LOST = 'LOST', '输单 (0%)'

    name = models.CharField(max_length=200, verbose_name='商机名称')
    
    # Customer Relationship
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='opportunities', verbose_name='客户', null=True, blank=True)
    customer_company = models.CharField(max_length=100, verbose_name='客户公司名称', blank=True, help_text='若未关联客户实体，可直接填写公司名')
    customer_contact_name = models.CharField(max_length=50, verbose_name='联系人姓名', blank=True)
    customer_email = models.EmailField(verbose_name='联系人邮箱', blank=True)
    customer_code = models.CharField(max_length=50, verbose_name='客户编号', blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='预计金额', null=True, blank=True)
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已回款金额')
    profit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='预计利润', null=True, blank=True)
    
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.CONTACT, verbose_name='阶段')
    
    description = models.TextField(blank=True, verbose_name='商机描述')
    competitors = models.TextField(blank=True, verbose_name='竞争对手')
    
    # People
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_opportunities', verbose_name='创建人')
    sales_manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_opportunities', verbose_name='销售负责人')
    
    # Team members (Many-to-Many via intermediate model for roles)
    team_members = models.ManyToManyField(User, through='OpportunityTeamMember', related_name='participated_opportunities', verbose_name='团队成员')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商机'
        verbose_name_plural = '商机列表'
        ordering = ['-created_at']

class OpportunityTeamMember(models.Model):
    """
    商机团队成员关联表
    """
    class Role(models.TextChoices):
        SALES = 'SALES', '销售'
        PRE_SALES = 'PRE_SALES', '售前/方案'
        SOLUTION = 'SOLUTION', '解决方案专家'
        DELIVERY = 'DELIVERY', '交付/实施'
        PROJECT_MANAGER = 'PM', '项目经理'
        PRODUCT_MANAGER = 'PDM', '产品经理'
        RND = 'RND', '研发'
        QA = 'QA', '测试'
        OTHER = 'OTHER', '其他'

    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, verbose_name='商机')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OTHER, verbose_name='角色')
    
    joined_at = models.DateTimeField(default=timezone.now, verbose_name='加入时间')

    class Meta:
        unique_together = ['opportunity', 'user']
        verbose_name = '团队成员'
        verbose_name_plural = '团队成员'

class OpportunityLog(models.Model):
    """
    商机跟进日志
    """
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='logs', verbose_name='商机')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    action = models.CharField(max_length=50, verbose_name='动作', help_text='例如：电话沟通、拜访、方案汇报')
    content = models.TextField(verbose_name='内容详情')
    
    # If this log represents a transfer of responsibility
    transfer_target = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transfers', verbose_name='移交给')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.opportunity.name} - {self.action} ({self.created_at})"

    class Meta:
        verbose_name = '跟进日志'
        verbose_name_plural = '跟进日志'
        ordering = ['-created_at']

# --- Extended Modules ---

class JobTitle(models.Model):
    """
    岗位名称配置 (Admins can maintain)
    """
    class Category(models.TextChoices):
        MANAGEMENT = 'MANAGEMENT', '管理'
        RND = 'RND', '研发'
        SALES = 'SALES', '销售'
        RESEARCHER = 'RESEARCHER', '研究员'
        MARKETING = 'MARKETING', '市场'
        OPERATION = 'OPERATION', '运营'
        DESIGN = 'DESIGN', '设计'
        SYSADMIN = 'SYSADMIN', '系统管理员'
        ASSISTANT = 'ASSISTANT', '助理' # Special role mentioned in user rules
        OTHER = 'OTHER', '其他'

    name = models.CharField(max_length=100, verbose_name='岗位名称')
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, verbose_name='岗位属性')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    class Meta:
        verbose_name = '岗位名称'
        verbose_name_plural = '岗位名称配置'
        unique_together = ['name', 'category']

class UserProfile(models.Model):
    """
    用户扩展信息
    """
    class Rank(models.TextChoices):
        ASSISTANT = 'ASSISTANT', '助理'
        SPECIALIST = 'SPECIALIST', '专员'
        SUPERVISOR = 'SUPERVISOR', '主任'
        MANAGER = 'MANAGER', '经理'
        DIRECTOR = 'DIRECTOR', '总监'
        DEPUTY_DIRECTOR = 'DEPUTY_DIRECTOR', '副总监'
        VP = 'VP', '副总裁'
        SVP = 'SVP', '高级副总裁'
        AP = 'AP', '助理总裁'
        PRESIDENT = 'PRESIDENT', '总裁'
    
    class RankLevel(models.TextChoices):
        NORMAL = 'NORMAL', '普通'
        SENIOR = 'SENIOR', '高级'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    
    # Deprecated fields (kept for migration safety, but logic moved to DepartmentModel)
    department = models.CharField(max_length=50, blank=True, verbose_name='部门(旧)')
    
    # New Department Link
    department_link = models.ForeignKey(DepartmentModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name='所属部门')
    
    report_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates_profiles', verbose_name='汇报对象')
    
    # New Job Fields
    job_category = models.CharField(max_length=20, choices=JobTitle.Category.choices, default=JobTitle.Category.OTHER, verbose_name='岗位属性')
    job_rank = models.CharField(max_length=20, choices=Rank.choices, blank=True, verbose_name='职级')
    job_rank_level = models.CharField(max_length=20, choices=RankLevel.choices, default=RankLevel.NORMAL, verbose_name='职级等级')
    
    # Replaced job_position with link to JobTitle (optional, string fallback allowed if needed but we prefer FK)
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='岗位名称')
    
    # Deprecated string field
    job_position = models.CharField(max_length=50, blank=True, verbose_name='职位(旧)', default='')
    job_level = models.CharField(max_length=20, blank=True, verbose_name='职级(旧)', default='', help_text='例如：P5, P6, M1')
    
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')

    def save(self, *args, **kwargs):
        # 自动从岗位名称同步岗位属性
        if self.job_title and self.job_title.category:
            self.job_category = self.job_title.category

        # Keep job_position in sync for legacy logic
        if self.job_title:
            self.job_position = self.job_title.name
        elif self.job_rank:
            self.job_position = self.get_job_rank_display()
        
        # Auto-generate email logic
        if not self.user.email:
            import pinyin
            # Simple pinyin conversion: zhangsan@...
            full_name = self.user.last_name + self.user.first_name
            if full_name:
                py_name = pinyin.get(full_name, format='strip', delimiter='')
                self.user.email = f"{py_name}@integritytech.com.cn"
                self.user.save()
        super().save(*args, **kwargs)

    def get_department_display(self):
        """
        获取部门显示名称 (兼容新旧字段)
        """
        if self.department_link:
            return self.department_link.name
        if self.department:
            return self.department
        return "-"
    
    def get_full_position_display(self):
        """
        Return e.g. "Senior Product Manager"
        """
        title = self.job_title.name if self.job_title else self.job_position
        if not title:
            return ""
            
        # Management category or President/VP ranks don't show "Level"
        if self.job_category == JobTitle.Category.MANAGEMENT:
            return title
            
        if self.job_rank in [self.Rank.PRESIDENT, self.Rank.VP, self.Rank.SVP]:
            return title
            
        # Otherwise show level if Senior
        if self.job_rank_level == self.RankLevel.SENIOR:
            return f"高级{title}"
        return title

    def __str__(self):
        return self.user.username

class PerformanceTarget(models.Model):
    """
    业绩指标 (KPI)
    """
    class TargetType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', '个人'
        DEPARTMENT = 'DEPARTMENT', '部门'
        COMPANY = 'COMPANY', '公司'

    class Period(models.TextChoices):
        MONTH = 'MONTH', '月度'
        QUARTER = 'QUARTER', '季度'
        YEAR = 'YEAR', '年度'

    target_type = models.CharField(max_length=20, choices=TargetType.choices, default=TargetType.INDIVIDUAL, verbose_name='指标类型')
    period = models.CharField(max_length=20, choices=Period.choices, default=Period.YEAR, verbose_name='周期类型')
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(null=True, blank=True, verbose_name='月份(仅月度)')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='季度(仅季度)')
    
    # Target Owner (One is required based on type)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='负责人')
    department = models.ForeignKey(DepartmentModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='负责部门', db_column='department')
    
    target_contract_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='新签合同目标')
    target_gross_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='回款毛利目标')
    target_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='确认收入目标')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '业绩指标'
        verbose_name_plural = '业绩指标'
        unique_together = ['target_type', 'period', 'year', 'month', 'quarter', 'user', 'department']

class Competition(models.Model):
    """
    赛事/活动信息
    """
    class Status(models.TextChoices):
        UPCOMING = 'UPCOMING', '即将开始'
        REGISTRATION = 'REGISTRATION', '报名中'
        ONGOING = 'ONGOING', '进行中'
        ENDED = 'ENDED', '已结束'

    name = models.CharField(max_length=200, verbose_name='赛事名称')
    organizer = models.CharField(max_length=100, verbose_name='主办方', blank=True, default='')
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    location = models.CharField(max_length=100, blank=True, verbose_name='地点')
    website = models.URLField(blank=True, verbose_name='官网')
    description = models.TextField(blank=True, verbose_name='详情描述')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING, verbose_name='状态')
    
    type = models.CharField(max_length=20, default='OTHER', verbose_name='赛事类型')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='负责人')

    # New Field
    challenge_count = models.IntegerField(default=0, verbose_name='赛题数量')

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def time(self):
        return self.start_date

    @property
    def owner_name(self):
        return self.owner.username if self.owner else ''

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '行业赛事'
        verbose_name_plural = '行业赛事'
        ordering = ['-start_date']

class MarketActivity(models.Model):
    """
    市场活动
    """
    name = models.CharField(max_length=200, verbose_name='活动名称')
    date = models.DateField(null=True, blank=True, verbose_name='活动日期')
    location = models.CharField(max_length=100, verbose_name='地点', blank=True, default='')
    participants = models.IntegerField(default=0, verbose_name='预计人数')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='预算')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='实际花费')
    
    leads_count = models.IntegerField(default=0, verbose_name='获客数量')
    
    type = models.CharField(max_length=20, default='OTHER', verbose_name='活动类型')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='负责人')
    description = models.TextField(blank=True, verbose_name='活动详情')
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def time(self):
        return self.date

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '市场活动'
        verbose_name_plural = '市场活动'
        ordering = ['-date']

class Announcement(models.Model):
    """
    公告/通知 (Will be deprecated/repurposed)
    """
    class Type(models.TextChoices):
        SYSTEM = 'SYSTEM', '系统公告'
        DEPARTMENT = 'DEPARTMENT', '部门公告'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', '草稿'
        PENDING = 'PENDING', '待确认/审核中'
        APPROVED = 'APPROVED', '已确认/已发布'
        REJECTED = 'REJECTED', '已驳回'

    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.DEPARTMENT, verbose_name='公告类型')
    
    # Deprecated: Using string for simplicity in older version, kept for compat
    department = models.CharField(max_length=20, choices=DepartmentModel.Category.choices, null=True, blank=True, verbose_name='所属部门')
    
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_announcements', verbose_name='发布人')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='状态')
    priority = models.CharField(max_length=10, default='MEDIUM', verbose_name='优先级')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'

class TodoTask(models.Model):
    """
    待办事项
    """
    class Priority(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
        
    class SourceType(models.TextChoices):
        MANUAL = 'MANUAL', '手动创建'
        AI_GENERATED = 'AI_GENERATED', 'AI生成'
        SYSTEM = 'SYSTEM', '系统触发'

    title = models.CharField(max_length=200, verbose_name='任务标题')
    description = models.TextField(blank=True, verbose_name='任务描述')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM, verbose_name='优先级')
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='所属用户')
    
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.MANUAL, verbose_name='来源类型')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '待办事项'
        verbose_name_plural = '待办事项'
        ordering = ['is_completed', '-priority', 'deadline']

class WorkReport(models.Model):
    """
    工作报告 (Weekly/Monthly) - Old version, might overlap with new DailyReport
    """
    class Type(models.TextChoices):
        WEEKLY = 'WEEKLY', '周报'
        MONTHLY = 'MONTHLY', '月报'

    report_type = models.CharField(max_length=10, choices=Type.choices, default=Type.WEEKLY, verbose_name='报告类型')
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    
    content = models.TextField(verbose_name='报告内容')
    plan_next = models.TextField(blank=True, verbose_name='下阶段计划')
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports', verbose_name='提交人')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.get_report_type_display()} ({self.start_date})"

    class Meta:
        verbose_name = '工作报告'
        verbose_name_plural = '工作报告'
        ordering = ['-start_date']

class SocialMediaAccount(models.Model):
    """
    社媒账号管理
    """
    class Platform(models.TextChoices):
        WECHAT_OFFICIAL = 'WECHAT_OFFICIAL', '微信公众号'
        WECHAT_VIDEO = 'WECHAT_VIDEO', '微信视频号'
        DOUYIN = 'DOUYIN', '抖音'
        BILIBILI = 'BILIBILI', 'Bilibili'
        WEIBO = 'WEIBO', '微博'
        XIAOHONGSHU = 'XIAOHONGSHU', '小红书'
        OTHER = 'OTHER', '其他'

    platform = models.CharField(max_length=20, choices=Platform.choices, default=Platform.OTHER, verbose_name='平台')
    account_name = models.CharField(max_length=100, verbose_name='账号名称', default='')
    account_id = models.CharField(max_length=100, blank=True, verbose_name='账号ID/Handle')
    
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='负责人')
    url = models.URLField(blank=True, verbose_name='主页链接')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_platform_display()} - {self.account_name}"

    class Meta:
        verbose_name = '社媒账号'
        verbose_name_plural = '社媒账号'
        unique_together = ['platform', 'account_name']

class SocialMediaStats(models.Model):
    """
    社媒数据统计 (每日/每周)
    """
    account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='stats', verbose_name='账号', null=True, blank=True)
    date = models.DateField(null=True, blank=True, verbose_name='统计日期')
    
    fans_count = models.IntegerField(default=0, verbose_name='粉丝数')
    fans_growth = models.IntegerField(default=0, verbose_name='粉丝增量')
    
    read_count = models.IntegerField(default=0, verbose_name='阅读/播放量')
    interaction_count = models.IntegerField(default=0, verbose_name='互动量(转评赞)')
    
    content_count = models.IntegerField(default=0, verbose_name='发布内容数')
    
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT, verbose_name='状态')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_stats', verbose_name='提交人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    def __str__(self):
        return f"{self.account} - {self.date}"

    class Meta:
        verbose_name = '社媒数据'
        verbose_name_plural = '社媒数据'
        unique_together = ['account', 'date']
        ordering = ['-date']

class ApprovalRequest(models.Model):
    """
    通用审批申请 (用于敏感操作或数据修改)
    """
    class Type(models.TextChoices):
        DATA_MODIFICATION = 'DATA_MODIFICATION', '数据修改'
        DELETE_REQUEST = 'DELETE_REQUEST', '删除申请'
        BUDGET_APPROVAL = 'BUDGET', '预算审批'
        OTHER = 'OTHER', '其他'
        
    request_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER, verbose_name='申请类型')
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING, verbose_name='状态')
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests', verbose_name='申请人')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_approvals', verbose_name='审批人')
    
    reason = models.TextField(verbose_name='申请详情/原因', default='', blank=True)
    feedback = models.TextField(blank=True, verbose_name='审批意见')
    
    # Link to related object (Generic FK)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Handle case where applicant might be used in older migrations/code
        username = self.applicant.username if self.applicant else 'Unknown'
        return f"{self.get_request_type_display()} - {username}"

    class Meta:
        verbose_name = '审批申请'
        verbose_name_plural = '审批申请'
        ordering = ['-created_at']

class ExternalIdMap(models.Model):
    class Entity(models.TextChoices):
        CUSTOMER = 'CUSTOMER', '客户'
        CONTACT = 'CONTACT', '联系人'
        OPPORTUNITY = 'OPPORTUNITY', '商机'
        SOCIAL_ACCOUNT = 'SOCIAL_ACCOUNT', '社媒账号'
    entity_type = models.CharField(max_length=30, choices=Entity.choices)
    object_id = models.IntegerField()
    system_name = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = [('system_name', 'external_id')]
        verbose_name = '外部ID映射'
        verbose_name_plural = '外部ID映射'

class ActivityLog(models.Model):
    class Type(models.TextChoices):
        OPPORTUNITY = 'OPPORTUNITY', '商机'
        CUSTOMER = 'CUSTOMER', '客户'
        CONTACT = 'CONTACT', '联系人'
        ACTIVITY = 'ACTIVITY', '活动'
        COMPETITION = 'COMPETITION', '赛事'
        PROJECT = 'PROJECT', '项目'
        DAILY_REPORT = 'DAILY_REPORT', '日报'
        SYSTEM = 'SYSTEM', '系统'
        USER = 'USER', '用户'

    type = models.CharField(max_length=20, choices=Type.choices)
    action = models.CharField(max_length=50, verbose_name='行为类型') # e.g. LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    content = models.TextField(verbose_name='日志内容')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    
    # 为了方便筛选，冗余部门信息
    department = models.CharField(max_length=100, blank=True, verbose_name='操作人部门')
    
    # GenericForeignKey to link to any object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '统一动态'
        verbose_name_plural = '统一动态'
        ordering = ['-created_at']

class SubmissionLog(models.Model):
    """
    自然语言解析与提交日志
    记录：输入文本、解析意图与实体、表单字段、执行结果、提交人与时间
    仅管理员可在“系统管理”板块查看与导出
    """
    class Status(models.TextChoices):
        PARSED = 'PARSED', '已解析'
        SUBMITTED = 'SUBMITTED', '已提交'
        FAILED = 'FAILED', '提交失败'
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='submission_logs', verbose_name='提交人')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PARSED, verbose_name='状态')
    text_input = models.TextField(verbose_name='原始输入')
    
    # New observability fields
    prompt = models.TextField(blank=True, verbose_name='完整Prompt')
    raw_response = models.TextField(blank=True, verbose_name='AI原始返回')
    error_message = models.TextField(blank=True, verbose_name='报错信息')
    
    intent = models.CharField(max_length=30, blank=True, verbose_name='意图')
    entity = models.CharField(max_length=30, blank=True, verbose_name='实体')
    fields = models.JSONField(default=dict, blank=True, verbose_name='表单字段')
    filters = models.JSONField(default=dict, blank=True, verbose_name='筛选条件')
    result_payload = models.JSONField(default=dict, blank=True, verbose_name='执行结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    class Meta:
        verbose_name = 'AI提交日志'
        verbose_name_plural = 'AI提交日志'
        ordering = ['-created_at']

class CustomerCohort(models.Model):
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_cohorts')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = '客户分群'
        verbose_name_plural = '客户分群'

# --- Project Management Models (Integrated from project_cards) ---

class Project(models.Model):
    """
    项目管理 (集成自 project_cards)
    """
    class Status(models.TextChoices):
        PLANNING = 'PLANNING', '规划中'
        IN_PROGRESS = 'IN_PROGRESS', '进行中'
        COMPLETED = 'COMPLETED', '已完成'
        PAUSED = 'PAUSED', '项目暂停'
        TERMINATED = 'TERMINATED', '项目终止'

    class Stage(models.TextChoices):
        # 规划中 (PLANNING)
        OPPORTUNITY = 'OPPORTUNITY', '商机阶段'
        PROPOSAL = 'PROPOSAL', '规划阶段'
        INITIATION = 'INITIATION', '立项阶段'
        
        # 进行中 (IN_PROGRESS)
        CONTRACT_SIGNED = 'CONTRACT_SIGNED', '已签合同'
        IMPLEMENTING = 'IMPLEMENTING', '实施阶段'
        ACCEPTANCE = 'ACCEPTANCE', '验收阶段'
        AFTER_SALES = 'AFTER_SALES', '售后阶段'
        PAYMENT_IN_PROGRESS = 'PAYMENT_IN_PROGRESS', '已经回款'
        
        # 已完成 (COMPLETED)
        # 注意：已完成阶段通常通过 is_revenue_confirmed 等布尔字段进一步细化，
        # 这里保留一个归档状态作为最终阶段
        ARCHIVED = 'ARCHIVED', '已归档'

    class Rhythm(models.TextChoices):
        DAILY = 'DAILY', '每日跟进'
        WEEKLY = 'WEEKLY', '每周跟进'
        BIWEEKLY = 'BIWEEKLY', '两周一跟'
        MONTHLY = 'MONTHLY', '每月跟进'
        AS_NEEDED = 'AS_NEEDED', '按需跟进'

    name = models.CharField(max_length=200, verbose_name='项目名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='项目编号', help_text='例如：CUST-PROJ-001')
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='关联客户')
    opportunity = models.ForeignKey('Opportunity', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='关联商机')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING, verbose_name='状态')
    stage = models.CharField(max_length=30, choices=Stage.choices, default=Stage.OPPORTUNITY, verbose_name='具体阶段')
    
    # Closing Checklist
    is_revenue_confirmed = models.BooleanField(default=False, verbose_name='已经确收')
    is_fully_paid = models.BooleanField(default=False, verbose_name='完全回款')
    is_maintenance_finished = models.BooleanField(default=False, verbose_name='维保完成')
    
    # Progress and Rhythm
    followup_rhythm = models.CharField(max_length=20, choices=Rhythm.choices, default=Rhythm.WEEKLY, verbose_name='跟进节奏')
    progress_manual = models.IntegerField(default=0, verbose_name='手动进度(%)')
    auto_update_progress = models.BooleanField(default=True, verbose_name='自动更新进度', help_text='勾选则根据卡片自动计算')
    
    description = models.TextField(blank=True, verbose_name='项目描述')
    
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='项目预算')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='owned_projects', verbose_name='负责人')
    members = models.ManyToManyField(User, related_name='participated_projects', blank=True, verbose_name='项目成员')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='扩展数据')
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # 记录状态或阶段变更日志
        if self.pk:
            try:
                old_obj = Project.objects.get(pk=self.pk)
                # 检查状态变更
                if old_obj.status != self.status:
                    # 仅在 operator 被显式传入时创建日志，或者通过视图层处理
                    pass
                # 检查阶段变更
                if old_obj.stage != self.stage:
                    pass
            except Project.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目列表'
        ordering = ['-created_at']

class ProjectDeleteLog(models.Model):
    """项目删除日志，用于管理员恢复"""
    project_name = models.CharField(max_length=200, verbose_name='原项目名称')
    project_code = models.CharField(max_length=50, verbose_name='项目编号')
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='删除人')
    deleted_at = models.DateTimeField(auto_now_add=True, verbose_name='删除时间')
    original_data = models.JSONField(verbose_name='原始数据备份')
    is_restored = models.BooleanField(default=False, verbose_name='是否已恢复')

    class Meta:
        verbose_name = '项目删除日志'
        verbose_name_plural = '项目删除日志'
        ordering = ['-deleted_at']

class ProjectChangeLog(models.Model):
    """
    项目信息变更日志
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='change_logs', verbose_name='关联项目')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    
    # 兼容字段
    action = models.CharField(max_length=50, verbose_name='动作', blank=True, default='')
    content = models.TextField(blank=True, verbose_name='内容详情', default='')
    
    # 原有字段 (保留兼容)
    field_name = models.CharField(max_length=50, verbose_name='变更字段', blank=True, default='')
    old_value = models.TextField(blank=True, verbose_name='旧值', default='')
    new_value = models.TextField(blank=True, verbose_name='新值', default='')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='变更时间')

    def __str__(self):
        return f"{self.project.name} - {self.field_name} - {self.created_at}"

    class Meta:
        verbose_name = '项目变更日志'
        verbose_name_plural = '项目变更日志'
        ordering = ['-created_at']

class ProjectCard(models.Model):
    """
    项目卡片 (任务/里程碑)
    """
    class Status(models.TextChoices):
        TODO = 'TODO', '待处理'
        DOING = 'DOING', '进行中'
        DONE = 'DONE', '已完成'
        BLOCKED = 'BLOCKED', '已阻塞'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cards', verbose_name='所属项目')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父卡片')
    
    title = models.CharField(max_length=200, verbose_name='卡片标题')
    content = models.TextField(blank=True, verbose_name='内容详情')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO, verbose_name='状态')
    sub_stage = models.CharField(max_length=50, blank=True, verbose_name='子项目阶段', help_text='例如：设计中、开发中、测试中')
    
    # 进度与预算
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='预算')
    man_days = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='工时(人天)')
    progress = models.IntegerField(default=0, verbose_name='进度(%)')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    deadline = models.DateField(null=True, blank=True, verbose_name='截止日期')
    
    assignees = models.ManyToManyField(User, related_name='assigned_cards', blank=True, verbose_name='负责人')
    
    # 里程碑标识
    is_milestone = models.BooleanField(default=False, verbose_name='是否里程碑')
    
    # 启用状态 (User Request: Enable/Disable cards)
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 排序
    order = models.IntegerField(default=0, verbose_name='排序')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='扩展数据')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 记录子阶段变更日志
        if self.pk:
            try:
                old_obj = ProjectCard.objects.get(pk=self.pk)
                # 检查子阶段变更
                if old_obj.sub_stage != self.sub_stage:
                    ProjectChangeLog.objects.create(
                        project=self.project,
                        operator=self.project.owner,  # 修正：使用 owner 而非 manager
                        field_name='sub_stage',
                        old_value=old_obj.sub_stage,
                        new_value=self.sub_stage
                    )
            except ProjectCard.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '项目卡片'
        verbose_name_plural = '项目卡片'
        ordering = ['order', 'created_at']

class DailyReport(models.Model):
    """
    工作日报
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', '草稿'
        SUBMITTED = 'SUBMITTED', '已提交'

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    date = models.DateField(verbose_name='日期')
    
    raw_content = models.TextField(verbose_name='原始工作内容', help_text='用户输入的原始记录')
    polished_content = models.TextField(blank=True, verbose_name='AI润色内容', help_text='AI优化后的总结')
    
    projects = models.ManyToManyField(Project, related_name='daily_reports', blank=True, verbose_name='关联项目')
    mentions = models.ManyToManyField(User, related_name='mentioned_reports', blank=True, verbose_name='提及用户')
    title = models.CharField(max_length=200, blank=True, default='', verbose_name='标题')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        verbose_name = '工作日报'
        verbose_name_plural = '工作日报'
        unique_together = ['user', 'date']
        ordering = ['-date']

class ContactDeleteLog(models.Model):
    """联系人删除日志，用于管理员恢复"""
    contact_name = models.CharField(max_length=100, verbose_name='原联系人姓名')
    customer_name = models.CharField(max_length=200, verbose_name='所属客户')
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='删除人')
    deleted_at = models.DateTimeField(auto_now_add=True, verbose_name='删除时间')
    original_data = models.JSONField(verbose_name='原始数据备份')
    is_restored = models.BooleanField(default=False, verbose_name='是否已恢复')

    class Meta:
        verbose_name = '联系人删除日志'
        verbose_name_plural = '联系人删除日志'
        ordering = ['-deleted_at']

    def __str__(self):
        return f"删除: {self.contact_name} ({self.customer_name})"

class SystemRelease(models.Model):
    version = models.CharField(max_length=50, verbose_name='版本号')
    title = models.CharField(max_length=200, verbose_name='版本标题')
    content = models.TextField(verbose_name='更新内容')
    release_date = models.DateField(default=timezone.now, verbose_name='发布日期')
    is_current = models.BooleanField(default=False, verbose_name='是否当前版本')
    status = models.CharField(max_length=20, default='RELEASED', verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '系统版本'
        verbose_name_plural = '系统版本'
        ordering = ['-release_date']

    def __str__(self):
        return f"{self.version} - {self.title}"
