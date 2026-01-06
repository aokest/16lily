# 测试报告：统一审批与活动流

## 概述
- 模块/主题：审批框架（ApprovalRequest）与活动中心（ActivityLog）
- 日期：2025-12-10
- 负责人：Trae AI

## 测试方法
- 环境：Docker 开发环境，`DEBUG=True`
- 账号：`admin_approval / manager_sales / manager_marketing / manager_game`（均密码 `123456`）
- 脚本：`python manage.py verify_approvals`

## 用例与POC

### 用例1：客户/商机审批 -> 销售经理
- 预期：自动生成审批指派到 `manager_sales`
- POC：
  - 获取token：`POST /api/api-token-auth/`
  - 查看待审批：`GET /api/approvals/`（使用 `manager_sales` token）
  - 执行审批：`POST /api/approvals/{id}/approve/`
- 实际：
  - `approvals#1 customer`、`approvals#2 opportunity` 指派 `manager_sales`；审批通过返回 200。
  - `GET /api/dashboard/activities/` 出现对应“审批通过 customer#7 / opportunity#14”。
- 修正：无

### 用例2：市场活动审批 -> 市场经理
- 预期：自动生成审批指派到 `manager_marketing`
- POC：同上（替换为市场经理token）
- 实际：`approvals#3 marketactivity` 指派 `manager_marketing`；通过返回 200；活动流显示“审批通过”。
- 修正：无

### 用例3：赛事审批 -> 春秋GAME经理
- 预期：自动生成审批指派到 `manager_game`
- POC：同上（替换为GAME经理token）
- 实际：`approvals#4 competition` 指派 `manager_game`；通过返回 200；活动流显示“审批通过”。
- 修正：无

## 回归测试
- 访问 `GET /api/dashboard/activities/`：已包含4条“审批通过”记录及创建事件；排序稳定且无500错误。

## 结论
- 是否通过：通过
- 建议：
  - 增加“审批驳回”记录展示；
  - 接入社媒粉丝审批路由；
  - 在大屏UI对审批类事件加上状态与颜色标签。

