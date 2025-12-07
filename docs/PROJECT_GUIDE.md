# 项目全景指南 (Project Guide)

> **最后更新时间**: 2025-12-06
> **版本**: v0.5.1-beta
> **说明**: 本文档旨在为 AI 助手和开发人员提供项目的全景视图、文件用途说明及修改注意事项。每次项目结构变更或完成重要功能迭代后，请务必更新本文档。

## 1. 项目概览 (Overview)

本项目是一个 **智能商机跟进及业绩统计系统 (CRM)**，基于 **Django** 框架开发，集成了 **DeepSeek/Ollama** 等大模型能力，用于自动化处理工作报告、商机录入、待办事项管理等业务。系统包含一个强大的后台管理系统（基于 Jazzmin 定制）和一个独立的前端数据大屏。

### 核心能力
- **业务管理**: 商机、客户、赛事、市场活动、待办事项的全生命周期管理。
- **AI 增强**: 对话式填单 (Chat-to-Form)、智能周报生成、自然语言解析。
- **数据可视化**: 组织架构全景图、业绩漏斗、实时战报大屏。

---

## 2. 目录结构与文件说明 (Directory Map)

### 📂 根目录 (`opportunity_system/`)
| 文件/目录 | 说明 | 注意事项 |
| :--- | :--- | :--- |
| `manage.py` | Django 命令行入口 | 用于运行服务、迁移数据库 (`migrate`)、创建用户等。 |
| `requirements.txt` | Python 依赖列表 | 添加新库后需更新此文件。 |
| `docker-compose.yml` | Docker 编排文件 | 用于本地开发环境的容器化部署。 |
| `.env.prod` | 环境变量配置 | 包含密钥、数据库连接等敏感信息 (生产环境用)。 |

### 📂 后端配置 (`backend/`)
| 文件 | 说明 | 修改建议 |
| :--- | :--- | :--- |
| `settings.py` | **核心配置文件** | 修改数据库、注册新 APP、配置中间件时修改此处。 |
| `jazzmin_settings.py` | **UI 配置文件** | 控制后台菜单结构、图标、顶部导航栏及主题色配置。 |
| `urls.py` | 全局路由入口 | 仅用于分发到各个 App 的 `urls.py`，尽量少写具体逻辑。 |

### 📂 核心业务模块 (`core/`)
这是项目的核心代码所在位置。

| 文件/目录 | 说明 | 关键逻辑/注意事项 |
| :--- | :--- | :--- |
| `models.py` | **数据模型定义** | 定义了 `Opportunity` (商机), `Customer` (客户), `AIConfiguration` (AI配置) 等核心表结构。**修改后必须执行 `makemigrations` 和 `migrate`**。 |
| `admin.py` | **后台管理逻辑** | 定义了 Admin 的列表页、详情页、过滤器及自定义 Action (如“导出CSV”)。 |
| `views.py` | **API 视图层** | 包含 `AIAnalysisView` (AI接口)、`DashboardView` (仪表盘数据) 等 DRF 视图。 |
| `urls.py` | 业务路由 | 定义 `api/` 开头的接口路径。 |
| `services/ai_service.py` | **AI 服务层** | **核心文件**。封装了调用 DeepSeek/Ollama 的逻辑。包含 `parse_opportunity` 等 Prompt 模板。修改 AI 行为时主要改这里。 |
| `signals.py` | 信号处理 | 处理模型保存前后的自动化逻辑 (如自动计算商机金额、更新日志)。 |
| `static/core/css/` | 自定义样式 | `custom_admin.css`: 包含“石榴红+金”主题的 CSS 变量覆盖。 |
| `management/commands/` | 自定义命令 | `init_demo_data.py`: 初始化演示数据脚本。 |

### 📂 模板层 (`templates/`)
用于覆盖 Django Admin 的默认界面或添加新页面。

| 路径 | 说明 |
| :--- | :--- |
| `admin/core/ai_change_form.html` | **通用 AI 填单模板**。所有支持 AI 对话的表单都继承此文件。包含前端 JS 调用 AI 接口的逻辑。 |
| `admin/core/departmentmodel/org_chart.html` | 组织架构全景图模板 (ECharts 实现)。 |
| `admin/core/*/kanban.html` | 各类看板视图 (赛事、市场活动)。 |

### 📂 前端大屏 (`frontend_dashboard/`)
这是一个独立于 Django 的静态网站，用于大屏展示。

| 文件 | 说明 |
| :--- | :--- |
| `index.html` | 战报大屏主页。 |
| `competitions.html` | 赛事看板大屏。 |
| `activities.html` | 市场活动看板大屏。 |
| `lib/` | 包含 Vue.js, ECharts, TailwindCSS 等静态资源。 |

### 📂 文档 (`docs/`)
| 文件 | 说明 |
| :--- | :--- |
| `PROJECT_GUIDE.md` | **本文件**。项目全景说明。 |
| `CHANGELOG.md` | 版本更新日志。 |
| `PRODUCT_SPEC.md` | 产品功能说明书。 |
| `TECHNICAL_DOCS.md` | 技术架构文档。 |
| `ROADMAP.md` | **新文件**。未来开发计划路线图。 |

---

## 3. 开发与修改指南 (Contribution Guide)

### 🛠 修改 AI 功能
1.  **增加新模型**: 
    - 在 `core/models.py` 的 `AIConfiguration.Provider` 枚举中添加新类型。
    - 在 `core/services/ai_service.py` 的 `_call_llm_json` 方法中配置该模型的 `base_url` 和请求头逻辑。
2.  **优化 Prompt**:
    - 直接修改 `core/services/ai_service.py` 中 `parse_xxx` 函数内的 `prompt` 字符串。
3.  **增加新的 AI 填单页面**:
    - 在 `core/admin.py` 中对应的 `ModelAdmin` 类下，设置 `change_form_template = 'admin/core/ai_change_form.html'`。
    - 在 `templates/admin/core/ai_change_form.html` 的 JS 逻辑中添加该模型的字段映射 (`fieldMapping`)。

### 🎨 修改 UI/主题
1.  **调整配色**: 修改 `core/static/core/css/custom_admin.css` 中的 CSS 变量 (`--pomegranate-primary`, `--gold-accent`)。
2.  **调整菜单**: 修改 `backend/jazzmin_settings.py`。

### 🗄 数据库变更
1.  修改 `core/models.py`。
2.  运行: `python manage.py makemigrations`
3.  运行: `python manage.py migrate`
4.  如果涉及老数据兼容，可能需要编写数据迁移脚本。

### ⚠️ 注意事项 (Caveats)
1.  **依赖管理**: 尽量保持 `core/services/ai_service.py` 零依赖 (使用 `urllib` 而非 `requests`)，以便在受限环境运行。
2.  **CSRF 保护**: 前端调用 API 时必须携带 `X-CSRFToken` (参考 `ai_change_form.html` 中的实现)。
3.  **文档同步**: **每轮修改结束后，AI 必须重新阅读并更新本文档 (`docs/PROJECT_GUIDE.md`)，确保文档与代码保持一致。**

---

## 4. 常用命令速查

```bash
# 启动后端服务 (默认端口 8000)
python manage.py runserver 0.0.0.0:8000

# 启动前端大屏 (临时测试，端口 8080)
cd frontend_dashboard
python -m http.server 8080

# 创建管理员用户
python manage.py createsuperuser

# 收集静态文件 (生产环境部署前)
python manage.py collectstatic
```
