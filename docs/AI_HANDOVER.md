# 🤖 AI 交接指南 (AI Handover Guide)

这份文档是为了帮助后续接手的 AI 助手快速理解环境、启动服务以及维护项目。

## 1. 🚀 快速启动 (Quick Start)

### 1.1 环境检查
当前项目主要运行在 **本地 Python 环境** 中（Docker 环境因网络问题暂时作为备选）。

- **Python 版本**: 3.11+
- **虚拟环境**: `venv`
- **依赖文件**: `requirements.txt`

### 1.2 启动服务
由于 Docker 网络受限，目前推荐使用 **本地多终端** 启动方式：

**Terminal 1: 后端服务 (Django)**
```bash
cd opportunity_system
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```
*   Admin后台: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
*   账号: `admin` / `admin` (或询问用户)

**Terminal 2: 前端大屏 (Simple HTTP Server)**
```bash
cd opportunity_system/frontend_dashboard
python3 -m http.server 8080
```
*   大屏地址: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

## 2. 🧠 AI 功能维护

### 2.1 架构说明
AI 功能的核心代码位于 `core/services/ai_service.py`。
- **支持模型**: DeepSeek (在线), Ollama (本地), OpenAI, Moonshot。
- **配置方式**: 在 Django Admin 后台 -> `系统配置` -> `AI模型配置` 中管理。

### 2.2 关键注意事项
1.  **CSRF 豁免**: 由于本地环境的特殊性，`/api/ai/analyze/` 接口在 `core/views.py` 中使用了 `@csrf_exempt` 和 `permission_classes = [AllowAny]` 以绕过 403 错误。在生产环境部署时，**务必**重新评估此安全性。
2.  **Ollama 本地连接**: 代码中包含对 `host.docker.internal` 和 `localhost` 的自动回退逻辑，以兼容 Docker 和本地环境。
3.  **JSON 清洗**: `_clean_and_parse_json` 方法专门用于处理小模型（如 Qwen-8b）可能输出的 Markdown 代码块或非标准 JSON。

## 3. 🐙 Git 维护指南

### 3.1 提交规范
每次完成一个完整的任务（Feature 或 Bugfix）后，**必须**进行提交。

```bash
git add .
git commit -m "Type: Description of changes"
git push origin main
```

**Type 示例**:
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `chore`: 杂项（如配置更新）

### 3.2 常见问题
- **Unrelated Histories**: 如果遇到 `fatal: refusing to merge unrelated histories`，使用：
  ```bash
  git pull origin main --allow-unrelated-histories
  ```
- **Privacy Email**: 用户的 GitHub 开启了隐私保护，Commit 时请使用 `aoke@users.noreply.github.com`（如果需要 Amend）。

## 4. 📝 待办事项 (Phase 4 Preview)
- **前后端分离**: 将 Dashboard 目前的静态 HTML 改造为 Vue 3 CLI 项目。
- **UI 组件库**: 引入 Ant Design Vue 或 Element Plus，替换 Django Admin 原生的简陋组件（特别是“增加用户”时的双选框）。
- **Docker 网络**: 彻底解决 Docker 容器内访问宿主机代理的问题，以便回归 Docker 部署。
