# 🤝 项目交接与开发指南 (Project Handover)

> **版本**: 2025-12-09
> **状态**: 正常 (Docker Environment Healthy)

本文档旨在帮助后续开发者快速接手项目，明确当前状态、已知问题及下一步计划。

## 1. 当前状态 (Current Status)

### 1.1 环境
- **Docker**: ✅ 已恢复。所有服务 (Web, DB, Dashboard) 运行正常。
- **Database**: PostgreSQL (Docker Container `opportunity_system-db-1`)。
- **Frontend**: Vue 3 Dashboard 运行在端口 `8080` (Docker)。
- **Backend**: Django Admin 运行在端口 `8000` (Docker)。

### 1.2 关键变更
- **商机移交逻辑**: 已从 Admin `save_model` 迁移至 `core/signals.py` (`post_save` on `OpportunityLog`)。测试脚本 `scripts/verify_transfer_check.py` 可用于验证。
- **前端配置**: `vite.config.ts` 已更新，支持通过 `BACKEND_URL` 环境变量动态配置代理目标。

## 2. 下一步计划 (Next Steps) - Phase 3 Priority

**核心任务**: 替换 Jazzmin Admin，构建现代化的 CRM 前端。

1.  **Vue CRM 模块开发**:
    - 在 `frontend_dashboard` 中新建 `src/views/crm/` 目录。
    - 开发 `OpportunityList.vue` (商机列表) 和 `OpportunityDetail.vue` (详情页)。
    - 对接后端 `OpportunityViewSet` API。
2.  **Auth 完善**:
    - 目前前端使用硬编码 Token (`src/api/index.ts`)。
    - 需要实现登录页面，获取 Token 并存储在 localStorage/Pinia 中。

## 3. 常用命令

```bash
# 启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f web
docker-compose logs -f dashboard

# 运行验证脚本
docker-compose exec web python scripts/verify_transfer_check.py

# 进入数据库
docker-compose exec db psql -U postgres -d opportunity_db
```

## 4. 已知问题 (Known Issues)
- **前端 Token**: 硬编码，需优先解决。
- **权限控制**: `DashboardViewSet` 目前使用了 `AllowAny` (为了方便调试)，上线前需改回 `IsAuthenticated`。

---
**致接手者**: 请优先阅读 `ROADMAP.md` 的 Phase 3 部分，这是用户的核心痛点。
