# 🤝 项目交接与开发指南 (Project Handover & Development Guide)

> **目标读者**: 新加入的开发人员、接手的 AI 助手、运维人员
> **版本**: 2.0 (2025-12-08 Updated)

本文档合并了原 `HANDOVER.md` 与 `AI_HANDOVER.md`，旨在提供一站式的环境搭建、启动与维护指南。

---

## 1. 🚀 快速启动 (Quick Start)

### 1.1 环境检查
*   **OS**: macOS (推荐), Linux, Windows (WSL2)
*   **Python**: 3.11+
*   **Node.js**: 18+ (用于前端 Vue 开发)
*   **Docker**: 推荐安装 Docker Desktop 以便容器化部署。

### 1.2 启动服务 (⚠️ Docker 模式暂不可用)
目前 Docker 环境存在 IPC 通信故障，**请暂勿使用**。修复后将恢复推荐。

### 1.3 启动服务 (✅ 推荐方式：本地开发)
目前推荐使用本地环境分别启动后端和前端：

## 1.4 测试规范 (New)
- 目录：`tests/`，包含 `reports/`、`pocs/`、`templates/`
- 每次开发后需产出测试报告：参考 `tests/templates/test-report-template.md`
- 示例报告：`tests/reports/2025-12-10-approvals.md`

**Terminal 1: 后端 (Django)**
```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
# 访问: http://127.0.0.1:8000/admin/
```

**Terminal 2: 前端 (Vue 3)**
```bash
cd frontend_dashboard
npm run dev -- --host
# 访问: http://127.0.0.1:8080/
```

---

## 2. 🗺️ 项目地图 (Project Map)

*   **`backend/`**: Django 项目配置 (`settings.py`, `urls.py`)。
*   **`core/`**: 核心业务应用。
    *   `models.py`: 数据模型 (Opportunity, Customer, etc.)。
    *   `services/ai_service.py`: AI 核心逻辑 (DeepSeek/Ollama 适配)。
    *   `admin.py`: 后台管理界面定制。
*   **`frontend_dashboard/`**: **[Phase 4 新增]** Vue 3 + Vite + Element Plus 前端项目。
*   **`docs/`**: 文档中心。

---

## 3. 🧠 AI 功能维护

### 3.1 架构说明
AI 功能位于 `core/services/ai_service.py`，支持多模型切换。
*   **配置**: 在 Django Admin -> `系统配置` -> `AI模型配置` 中管理。
*   **提示词**: 在 Django Admin -> `系统配置` -> `提示词模板` 中管理。

### 3.2 关键注意事项
1.  **CSRF 豁免**: 为解决本地开发时的 403 问题，`/api/ai/analyze/` 接口使用了 `@csrf_exempt`。生产环境需重新评估。
2.  **Ollama 连接**: 代码内置了对 `host.docker.internal` 和 `localhost` 的自动回退机制，以适应 Docker 和本地环境。
3.  **JSON 清洗**: 针对小模型（如 Qwen-8b）的输出，系统会自动清洗 Markdown 标记。

---

## 4. 🐙 Git 维护规范

*   **Commit Message**: `Type: Description` (e.g., `feat: Add Vue dashboard`, `fix: Fix CSRF error`)
*   **Unrelated Histories**: 若遇到合并错误，使用 `git pull origin main --allow-unrelated-histories`。

---

## 5. 📚 文档索引
*   **协作规范**: [AI_COLLABORATION_GUIDE.md](../ai/AI_COLLABORATION_GUIDE.md) (AI 必读)
*   **开发日志**: [DEV_LOG.md](../DEV_LOG.md) (记录每日变更)
*   **未来规划**: [ROADMAP.md](../planning/ROADMAP.md) (查看下一步计划)
4.  **AI对话规划**：详见 `docs/AI_DIALOGUE_ARCHITECTURE.md`；未来将提供统一 `POST /api/chat/` 接口，实现对话式创建/更新/审批与查询。
