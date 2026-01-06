# AI 对话式集成架构规划

## 目标
在单一对话窗口内完成：商机/客户/赛事/市场的创建与更新、数据与知识的查阅、申请与审批；并遵守用户权限与部门边界。

## 数据域与权限
- 主体：Opportunity, Customer, Competition, MarketActivity, SocialMediaStats, ApprovalRequest, ActivityLog, TodoTask, WorkReport, Announcement
- 用户：User + UserProfile(job_role, department_link, reports_to)
- 部门：DepartmentModel（支持树状层级，manager为负责人）
- 权限原则：
  - 管理员最高越权；
  - 员工默认仅访问本人负责/参与及本部门允许的数据；
  - 审批与申请通过 `ApprovalRequest` 管理；所有动作写入 `ActivityLog`。

## 统一对话接口（草案）
- Endpoint：`POST /api/chat/`（后续实现）
- 请求结构：
  - `intent`: `create | update | get | approve | reject | list`
  - `entity`: `opportunity | customer | competition | marketactivity | approval | knowledge`
  - `fields`: `{...}`（创建/更新字段）
  - `filters`: `{...}`（查询条件）
  - `context`: `{ user_id, department, role }`
- 响应结构：
  - `result`: 结构化对象或列表
  - `actions`: 后续建议/可选下一步
  - `audit_id`: 写入 `ActivityLog` 的事件编号

## 角色到能力映射
- `ADMIN`：所有实体的CRUD、审批、越权；
- `DIRECTOR/VICE_DIRECTOR`：本军团/部门域内数据读写与审批；
- `MANAGER`：本部门数据读写与审批；
- `MEMBER/SALES_REP/…`：本人负责的数据读写与申请，审批由上级完成。

## 安全与审计
- 操作全部写入 `ActivityLog`；审批通过/驳回产生事件；
- 请求携带 `Token`；后端根据 `UserProfile` 与 `DepartmentModel` 计算授权；
- 敏感操作（审批、移交）需二次确认或对话澄清。

## 分阶段实现
1. Phase A：对话接口 `chat` 的路由与基本解析、与现有 API 的适配器层（已上线 `POST /api/chat/`，支持审批列表/通过/驳回、客户创建、商机列表）；
2. Phase B：权限检查与错误提示标准化；
3. Phase C：知识检索（FAQ/文档/公告）与数据分析（统计、趋势、漏斗）；
4. Phase D：UI集成到大屏与CRM页，支持上下文会话与卡片式回填。
