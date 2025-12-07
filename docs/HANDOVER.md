# 🤝 项目交接指南 (Handover Guide)

> **适用对象**: 新加入的开发人员、接手的 AI 助手、运维人员
> **环境要求**: macOS (Apple Silicon 推荐), Python 3.11+, Docker Desktop

欢迎接手 **团队商机与业绩跟进系统**。这份指南将帮助你以最快速度跑通项目，理解上下文，并开始贡献代码。

---

## 1. 快速上手 (Getting Started)

### 1.1 环境准备
本项目依赖 **Python 3.11** 和 **PostgreSQL**。我们推荐使用 Docker 运行数据库，本地运行 Django 服务。

1.  **克隆代码**:
    ```bash
    git clone <repository_url>
    cd opportunity_system
    ```

2.  **启动数据库 (Docker)**:
    确保已安装 Docker Desktop。
    ```bash
    docker-compose up -d db
    ```
    *这将启动一个 PostgreSQL 15 容器，端口映射为 5432。*

3.  **设置 Python 环境**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **初始化数据库**:
    ```bash
    python manage.py migrate
    python manage.py init_roles      # 初始化权限组
    python manage.py init_demo_data  # (可选) 写入测试数据
    python manage.py createsuperuser # 创建你的管理员账号
    ```

5.  **启动服务**:
    ```bash
    ./start_dev.sh
    ```
    *访问 http://127.0.0.1:8000/admin/*

---

## 2. 项目地图 (Project Map)

不要被文件数量吓到，核心逻辑只在以下几个地方：

- **业务逻辑**: 都在 `core/` 目录下。
    - `models.py`: 数据库表结构（改这里要迁移数据库）。
    - `admin.py`: 后台界面的配置（改这里影响后台长什么样）。
    - `services/ai_service.py`: AI 相关的逻辑（调用 DeepSeek/Ollama 等）。
- **配置中心**: `backend/settings.py` (后端配置) 和 `backend/jazzmin_settings.py` (UI配置)。
- **数据大屏**: `frontend_dashboard/` 是一个独立的前端项目（Vue + ECharts），目前是静态的，正在进行 API 对接。

详细的文件说明请查阅 [PROJECT_GUIDE.md](PROJECT_GUIDE.md)。

---

## 3. 常见任务指引 (How-To)

### Q: 如何修改商机字段？
1.  修改 `core/models.py` 中的 `Opportunity` 类。
2.  运行 `python manage.py makemigrations`。
3.  运行 `python manage.py migrate`。
4.  重启服务。

### Q: 如何调整 AI 的提示词 (Prompt)？
**注意**: 现在的 Prompt 已不在代码中硬编码。
1.  登录后台管理系统 `/admin/`。
2.  进入 **系统配置 -> 提示词模板**。
3.  找到对应的场景（如 `OPPORTUNITY`），修改其内容并保存。
4.  系统会自动读取最新且启用的模板。

### Q: 大屏数据不显示？
目前大屏主要展示 Mock 数据。如果需要对接真实数据，请检查 `frontend_dashboard/index.html` 中的 JS 逻辑，确保 API 地址指向 `http://127.0.0.1:8000/api/...` 并且解决了跨域 (CORS) 问题。

---

## 4. 注意事项与坑 (Pitfalls)

1.  **静态文件**: 生产环境部署前必须运行 `python manage.py collectstatic`，否则后台样式会丢失。
2.  **数据库连接**: 本地开发使用 `localhost`，但如果是 Docker 内部互联（如 Django 也在 Docker 中），请使用 `db` 作为主机名。
3.  **AI 依赖**: `ai_service.py` 尽量使用标准库 `urllib`，避免引入过多第三方依赖，以保持轻量和易移植。
4.  **Ollama 超时**: 本地小模型（如 Qwen3:8b）响应较慢，AI Service 已将超时时间设为 60秒，请勿随意改短。

---

## 5. 文档体系 (Documentation)

- **想了解项目背景?** -> [PROJECT_TRACKING.md](PROJECT_TRACKING.md)
- **想看技术细节?** -> [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)
- **想看未来计划?** -> [ROADMAP.md](ROADMAP.md)
- **想知道如何与 AI 协作?** -> [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md)

---

**Happy Coding! 🚀**
