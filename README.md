# 🚀 石榴粒粒 (16Lily) - 综合业务管理系统

> **数字化作战指挥中心**：打破部门壁垒，让每一个角色的贡献都被看见。

---

## 📚 文档导航 (Documentation Index)

本项目拥有完善的文档体系，请根据您的角色选择阅读入口：

### 👨‍💻 开发人员 / 接手者 (Developers)
- **👉 [开发指南 (Development Guide)](docs/DEVELOPMENT.md)**: **必读！** 环境搭建、代码地图、AI 模块维护与 Git 规范。
- **🤖 [AI 协作指南 (AI Copilot Guide)](docs/AI_COLLABORATION_GUIDE.md)**: 教你如何与 Trae/AI 高效协作。
- **🛠 [技术架构 (Technical Docs)](docs/TECHNICAL_DOCS.md)**: 深入了解架构设计、API 规范。
- **🗺 [项目全景 (Project Guide)](docs/PROJECT_GUIDE.md)**: 详细的文件目录说明与开发规范。

### 👔 产品经理 / 业务负责人 (Product Owners)
- **📈 [项目追踪 (Project Tracking)](docs/PROJECT_TRACKING.md)**: **核心文档**。包含项目初衷、目标、当前进度与下一步计划。
- **📖 [产品功能书 (Product Spec)](docs/PRODUCT_SPEC.md)**: 详细的功能定义与业务流程。
- **🗺️ [路线图 (Roadmap)](docs/ROADMAP.md)**: 未来的开发规划 (含 Phase 3 前后端分离)。

### 👥 最终用户 (End Users)
- **📘 [用户操作手册 (User Manual)](docs/USER_MANUAL.md)**: 分角色操作指引（销售、经理、管理员）。

### 🔧 运维人员 (Ops)
- **⚙️ [维护手册 (Maintenance)](docs/MAINTENANCE.md)**: 部署、备份、安全加固指南。

---

## ⚡️ 快速开始 (Quick Start)

仅需 3 步即可启动本地开发环境（详细步骤请参阅 [交接指南](docs/HANDOVER.md)）：

1.  **启动数据库**:
    ```bash
    docker-compose up -d db
    ```
2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **运行服务**:
    ```bash
    ./start_dev.sh
    ```
    *后台地址: http://127.0.0.1:8000/admin/*

---

## 🏗 系统架构简述

- **后端**: Python 3.11 + Django 4.2 + DRF
- **数据库**: PostgreSQL 15 (Docker)
- **后台 UI**: Jazzmin (基于 Django Admin)
- **大屏前端**: Vue.js + ECharts (独立静态页)
- **AI 引擎**: 集成 DeepSeek/Ollama 用于智能填单与分析

---

## 📝 最新状态
> 更多详情请查看 [PROJECT_TRACKING.md](docs/PROJECT_TRACKING.md)

- **当前版本**: Phase 2 (核心业务与大屏)
- **最近更新**:
    - **AI 增强**: 修复 Ollama 连接与解析问题，支持 Qwen3:8b。
    - **Prompt 管理**: 实现后台可配置的 PromptTemplate。
    - **文档重构**: 建立完整的文档闭环体系。
