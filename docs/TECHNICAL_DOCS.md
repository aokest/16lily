# 技术架构与开发文档

## 1. 系统架构

本系统采用 **前后端分离** 的混合架构模式：
- **管理后台 (Admin)**：基于 Django Admin 二次开发，采用传统的 SSR (Server-Side Rendering) 模式。
- **数据大屏 (Dashboard)**：基于 Vue.js + ECharts 的纯静态前端页面，通过 REST API 与后端通信。
- **API 服务**：Django REST Framework 提供标准 JSON 接口。

### 技术栈
- **后端**：Python 3.11 + Django 4.2
- **API框架**：Django REST Framework (DRF)
- **数据库**：PostgreSQL 15
- **后台UI**：Jazzmin (基于 Bootstrap 4 的 Django Admin 主题)
- **大屏前端**：Vue 3 (CDN模式) + TailwindCSS + ECharts 5
- **部署**：Docker + Docker Compose + Nginx

## 2. 目录结构说明

```text
opportunity_system/
├── backend/                # Django 项目配置
│   ├── settings.py         # 核心配置 (CORS, Apps, DB)
│   └── urls.py             # 根路由
├── core/                   # 核心业务应用
│   ├── models.py           # 数据模型定义 (商机, 赛事, 客户等)
│   ├── admin.py            # 后台管理逻辑 (自定义Action, 看板视图)
│   ├── views.py            # API 视图 (ViewSets)
│   ├── serializers.py      # API 序列化器
│   ├── services/           # [新增] 业务逻辑层
│   │   └── ai_service.py   # [新增] LLM 调用与 JSON 解析服务
│   └── urls.py             # API 路由
├── frontend_dashboard/     # 大屏前端代码 (独立运行)
│   ├── competitions.html   # 赛事大屏
│   ├── activities.html     # 活动大屏
│   └── lib/                # 静态依赖库 (Vue, ECharts)
├── templates/              # Django 模板重写
│   └── admin/              # 覆盖原生的 Admin 模板
│       └── core/
│           └── ai_change_form.html # AI 辅助填单组件
├── static/                 # 静态资源 (CSS/JS)
├── docs/                   # 项目文档
├── scripts/                # 维护脚本 (update.sh, backup.sh)
├── docker-compose.yml      # 开发环境容器配置
└── docker-compose.prod.yml # 生产环境容器配置
```

## 3. 核心模块实现细节

### 3.1 自定义 Admin 视图 (看板)
Django Admin 原生只支持列表视图 (`change_list`)。我们通过以下方式实现了 Kanban 看板：
1.  在 `admin.py` 中重写 `get_urls` 方法，注入自定义 URL (如 `kanban/`)。
2.  编写自定义视图方法 (如 `kanban_view`)，获取数据并渲染自定义模板。
3.  创建模板 `templates/admin/core/competition/kanban.html`，继承 `admin/base_site.html` 以保持风格一致。

### 3.2 权限控制 (RBAC)
系统摒弃了复杂的 Django Group 机制，在 `UserProfile` 中定义了 `department_link` (关联部门) 和 `job_role` (岗位)。
- **行级权限**：在 `ModelAdmin.get_queryset` 中过滤，普通销售只能看自己的客户。
- **操作权限**：在 `admin.py` 的 `approve_opportunity` 等 Action 中，通过代码逻辑检查 `user.profile.department` 是否匹配。

### 3.3 前后端通信
- **跨域 (CORS)**：在 `backend/settings.py` 中启用了 `django-cors-headers` 并允许所有来源 (`CORS_ALLOW_ALL_ORIGINS = True`)，以便前端大屏 (Port 8080) 能访问 API (Port 8000)。
- **认证**：API 启用了 `BasicAuthentication`。前端在 Axios 请求头中携带 Base64 编码的用户名密码。

### 3.4 AI 接口配置
- **模型**：`core.models.AIConfiguration`
- **逻辑**：支持多个模型配置，通过 `is_active=True` 标记默认使用的模型。
- **扩展**：`AIService` 会优先使用前端传入的 `config_id`，如果未传则使用系统默认配置。

### 3.5 AI 业务集成 (Chat-to-Form)
系统实现了基于 **对话式 AI** 的智能填单功能，完全取代了旧版的“原始文本字段”方案。

- **前端交互**: 
    - 使用 `templates/admin/core/ai_change_form.html` 覆盖 Django Admin 的默认表单模板。
    - 嵌入了一个 AI 聊天组件，用户输入自然语言后，通过 Fetch API 调用 `/api/ai/analyze/` 接口。
- **后端处理**:
    - **API**: `core.views.AIAnalyzeView` 接收文本和场景类型 (如 `OPPORTUNITY`)。
    - **Service**: `core.services.ai_service.AIService` 负责构建 Prompt 并调用 LLM。
    - **JSON 解析**: 针对 Qwen 等小模型优化了解析逻辑，能自动提取非标准格式中的 JSON 数据。
- **自动填充**: 前端收到 JSON 响应后，通过 JavaScript 自动将数据填入表单对应的 Input 或 Select2 组件中。

### 3.6 提示词管理 (Prompt Management)
为了避免硬编码，系统实现了 `PromptTemplate` 模型。
- **动态查找**: `AIService._get_prompt(scene)` 会自动查找该场景下**最新且启用**的模板。
- **后台管理**: 管理员可以在 `/admin/core/prompttemplate/` 实时调整提示词，无需重启服务。

### 3.7 数据大屏 API (Dashboard)
大屏通过以下两个核心 API 获取实时数据：

#### 1. 统计数据 (`/api/dashboard/stats/`)
- **Method**: `GET`
- **Params**: `department` (可选, 如 `SALES`)
- **Response**:
  ```json
  {
      "financials": {
          "actual_signed": 1500000,
          "target_signed": 2000000,
          "actual_return_profit": 800000,
          "target_return_profit": 1000000,
          "actual_revenue": 1200000,
          "target_revenue": 1500000
      },
      "funnel": {
          "total_pipeline_amount": 5000000,
          "total_count": 45
      },
      "stages": [
          {"stage": "CONTACT", "count": 10},
          {"stage": "WON", "count": 5}
      ],
      "new_counts": {
          "today": 2, "week": 5, "month": 12
      }
  }
  ```

#### 2. 实时动态 (`/api/dashboard/activities/`)
- **Method**: `GET`
- **Params**: `department` (可选)
- **Response**: 返回最新的 20 条 `OpportunityLog` 记录。

## 4. 数据库设计重点

### 4.1 组织架构
采用 **DepartmentModel** (自引用外键) 实现无限层级的树状组织架构。
- 字段：`parent` (FK to self), `manager` (FK to User), `category` (部门性质)。

### 4.2 商机 (Opportunity)
核心字段：
- `stage` (阶段): 接触 -> 赢单
- `amount` (预计金额) vs `signed_amount` (合同金额)
- `customer` (FK to Customer): 关联客户主体

## 5. 部署与维护

请参考同目录下的 `MAINTENANCE.md` 文档，其中包含：
- 生产环境部署步骤
- 更新脚本使用方法 (`./scripts/update.sh`)
- 数据库备份与恢复
- 安全配置 (Nginx, Docker Network)

## 6. 常见问题 (FAQ)

**Q: 为什么修改了 models.py 后后台报错？**
A: Django 模型修改后必须运行迁移。请执行：
```bash
python manage.py makemigrations
python manage.py migrate
```

**Q: 大屏页面显示 401 Unauthorized？**
A: 前端页面硬编码了测试账号 (admin/admin123456)。生产环境需修改 `frontend_dashboard/*.html` 中的 Axios Auth Header 配置，或改为 Token 认证。

**Q: 静态文件 404？**
A: 生产环境由 Nginx 代理静态文件。请确保运行了 `python manage.py collectstatic` (在 `update.sh` 中已自动包含)。
