# 变更日志 (Changelog)

> **项目**: 智能商机跟进及业绩统计系统
> **维护者**: Trae AI Assistant

## v0.6.0-beta (2025-12-09)

### 🚀 架构升级 (Architecture)
- **环境恢复**: 成功修复 Docker 守护进程连接问题，将数据库配置从 SQLite 临时模式切回 Docker/PostgreSQL。
- **信号重构 (Refactor)**: 将 "商机移交" 的业务逻辑从 `admin.py` 迁移至 `core/signals.py`。
    - 优势：解耦了 Admin 界面与业务逻辑，确保未来通过 API (Vue前端) 也可以触发同样的移交审批流程。
- **前端兼容性**: 修复 Vite/Tailwind v4 在 Docker 环境下的网络连接与构建配置问题。

### 📋 规划更新 (Roadmap)
- **Phase 3启动**: 正式确立 "去 Jazzmin 化" 战略。
    - 目标：逐步将核心 CRM 功能（商机管理、跟进记录）迁移至 Vue 3 Dashboard。
    - 现状：后端已就绪 (DRF + Signals)，前端已就绪 (Vue + Element Plus)。

---

## v0.5.4-beta (2025-12-07)
... (Previous logs)
