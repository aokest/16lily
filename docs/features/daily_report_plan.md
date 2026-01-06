# 日报功能 (Daily Report) 规划方案

## 1. 功能概述 (Feature Overview)
为用户提供一个集成的日报管理工具，允许用户按日历维度记录每日工作内容，关联相关项目，并利用AI对内容进行润色，生成符合不同岗位（研发、销售、管理）视角的专业总结。

## 2. 用户故事 (User Stories)
*   **作为一名员工**，我希望在个人中心或快捷菜单中找到“日报”入口，以便快速开始填写。
*   **作为一名员工**，我希望在填写日报时能通过“@”符号快速关联我参与的项目，以便系统自动归集项目工时或进度。
*   **作为一名员工**，我希望能点击“AI润色”按钮，让AI根据我流水账式的记录，自动整理成结构清晰、语气专业的日报，节省我的思考时间。
*   **作为一名管理者**，我希望能查看团队成员的日报，并按项目维度聚合查看该项目的所有相关日报，了解项目每日进展。

## 3. 核心功能设计 (Core Features)

### 3.1 入口与布局
*   **侧边栏入口**: 在 Dashboard 侧边栏“个人中心”下增加“我的日报”菜单。
*   **AI中枢入口**: 在 AI 中枢的功能区增加“写日报”快捷卡片。
*   **日历视图**: 进入后默认展示月度日历热力图，显示每日日报提交状态（已提交/未提交/草稿）。

### 3.2 编辑器体验
*   **富文本编辑器**: 支持基础格式，核心支持 `@ProjectName` 的提及功能。
*   **智能关联**: 输入 `@` 时触发项目下拉列表（优先显示用户参与的进行中项目）。
*   **结构化字段**:
    *   日期 (Date)
    *   工时 (Man-hours)
    *   工作内容 (Raw Content)
    *   困难与协助 (Blockers)
    *   明日计划 (Next Steps)

### 3.3 AI 智能润色 (AI Polish)
*   **场景识别**: 系统根据用户的岗位信息（如研发、销售、产品），调用不同的 Prompt 模板。
    *   *研发*: 侧重技术实现、Bug修复、性能优化结果。
    *   *销售*: 侧重客户触达、商机推进、回款进度。
    *   *管理*: 侧重团队协调、风险管控、资源分配。
*   **一键生成**: 用户输入关键词或口语化描述，AI 生成标准化段落。

## 4. 技术架构 (Technical Architecture)

### 4.1 数据库设计 (Database Schema)

```python
class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    date = models.DateField(default=timezone.now)
    
    # 内容
    raw_content = models.TextField(help_text="用户原始输入")
    polished_content = models.TextField(help_text="AI润色后的内容", blank=True)
    
    # 关联
    projects = models.ManyToManyField('Project', related_name='daily_reports', blank=True)
    
    # 状态
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('SUBMITTED', '已提交'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
```

### 4.2 API 接口 (API Endpoints)
*   `GET /api/daily-reports/`: 获取列表（支持日期范围过滤）。
*   `GET /api/daily-reports/calendar/`: 获取日历状态数据。
*   `POST /api/daily-reports/`: 创建/保存草稿。
*   `POST /api/daily-reports/{id}/polish/`: 触发 AI 润色。
    *   Input: `raw_content`, `user_role`
    *   Output: `polished_content`

### 4.3 前端组件 (Frontend Components)
*   `DailyReportCalendar`: 日历组件，展示状态。
*   `ReportEditor`: 编辑器，集成 `@` 提及功能 (可使用 `tiptap` 或 `quill` 插件)。
*   `AIPolishButton`: 调用润色接口并流式展示结果。

## 5. 开发计划 (Development Roadmap)
1.  **Phase 1 (后端基础)**: 创建模型，API 接口，管理后台。
2.  **Phase 2 (前端核心)**: 日历视图，基础编辑器，CRUD 流程。
3.  **Phase 3 (AI 集成)**: 接入 DeepSeek/Gemini API，开发 Prompt 模板，实现润色功能。
4.  **Phase 4 (项目关联)**: 实现编辑器 `@` 提及交互，后端自动解析关联项目。
