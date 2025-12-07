# 🛠️ 开发日志 (Development Log)

记录项目的开发历程、关键决策及下一步计划。

## 📅 2025-12-08: 系统修复与AI功能增强 (Phase 3.1)
- **核心修复**:
    - **用户管理**: 修复了“增加用户”页面因 `department` 字段只读导致的崩溃问题。
    - **大屏展示**: 修复了 LIVE INTEL 模块在数据较少时不滚动的问题；解决了大屏不显示历史商机的问题（通过脚本回填了缺失的日志）。
    - **商机录入**: 修复了“增加商机”时因 `OpportunityLog` 引用错误导致的 NameError。
- **AI 智能集成 (DeepSeek/Ollama)**:
    - **模型配置**: 修复了 DeepSeek API 地址硬编码错误（改为 `https://api.deepseek.com`）。
    - **本地大模型支持**: 增强了对 Ollama 本地服务的连接稳定性，增加了 `host.docker.internal` 与 `localhost` 的自动回退机制。
    - **鲁棒性增强**: 
        - 重写了 JSON 解析逻辑，能够自动剥离 Markdown 代码块，兼容小模型（如 Qwen-8b）的非标准输出。
        - 增加了详细的错误透传机制，前端能直接显示 API 连接超时、鉴权失败等具体红字报错，不再“静默失败”。
        - 为 AI 接口 (`/api/ai/analyze/`) 添加了 `csrf_exempt` 豁免，解决了本地开发环境下的 403 Forbidden 问题。
- **遇到的挑战与经验**:
    - **Docker 网络**: Docker 容器内访问宿主机服务（如 Ollama）需要特殊处理 (`host.docker.internal`)，且受限于本地代理配置。
    - **CSRF 防御**: 前后端分离（或类分离）架构中，Django 的 CSRF 校验在本地 `localhost` 环境下格外严格，必要时需对特定 API 豁免。
    - **AI 输出不可控**: 即使是 Prompt 约束，小模型仍可能输出“废话”包裹 JSON，必须在代码层做清洗。
- **下一步**:
    - 推进 Phase 4：完全的前后端分离改造。
    - 优化权限配置界面的 UI（计划引入 Ant Design Transfer 组件）。

## 📅 2025-12-05: 系统优化与Bug修复 (Phase 2)
- **前端优化 (Dashboard)**:
    - 修复 "Live Intel" 动态播报右侧被截断的布局问题 (`index.html`)。
    - 修复主题切换器 (Theme Switcher) 失效的问题，现在能正确切换 CSS 主题。
- **后端/Admin 优化**:
    - 修改系统 Header 为 "石榴经营"。
    - 修复 Admin 侧边栏溢出无法滚动的问题 (CSS)。
    - 修复 Admin 成功消息 (Green Alert) 文字对比度不足的问题。
    - 为 `OpportunityLogAdmin` 添加批量导出 CSV 功能。
- **业务逻辑增强**:
    - `Opportunity` 模型：
        - 保存时若 `revenue` (确认收入) 为空，自动填充为 `signed_amount` (签约金额)。
        - 保存时自动将 `sales_manager` (负责销售) 添加到 `OpportunityTeamMember` 项目组成员列表中，角色设为销售经理。

## 📅 2025-12-05: 项目启动 (Phase 1)
- **动作**: 初始化项目结构。
- **决策**: 
    - 选用 **Django** 作为后端框架，因其内置强大的 Admin 后台和 ORM，适合快速开发企业级应用。
    - 选用 **PostgreSQL** + **Docker** 作为数据存储方案，方便本地开发与云端部署的统一。
    - 确定采用 **前后端分离** 架构，前端使用 Vue 3。
- **下一步**: 
    - 配置 Docker 环境运行数据库。
    - 初始化 Django 项目骨架。
    - 设计核心数据库模型（用户、商机）。
