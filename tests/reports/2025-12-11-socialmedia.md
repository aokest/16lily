# 测试报告：社媒粉丝审批接入

## 概述
- 模块/主题：SocialMediaStats 审批接入与活动流
- 日期：2025-12-11
- 负责人：Trae AI

## 测试方法
- 环境：Docker 开发环境，`DEBUG=True`
- 账号：`manager_marketing`（密码 `123456`）
- 脚本：`python manage.py verify_socialmedia`

## 用例与POC
- 用例：创建社媒粉丝记录，状态为 `PENDING`，自动生成审批并写入活动流
- POC：
  - 运行：`docker-compose exec web python manage.py verify_socialmedia`
  - 预期：输出 `Created SocialMediaStats#<id>, approvals=1`
  - 查看待审批：`GET /api/approvals/` 使用市场经理 token
  - 审批通过：`POST /api/approvals/{id}/approve/` JSON: `{"reason":"同意(社媒)"}`
  - 活动流：`GET /api/dashboard/activities/` 显示“审批通过 socialmediastats#<id> 同意(社媒)”

## 实际结果
- 控制台输出：`Created SocialMediaStats#<id>, approvals=1`
- 待审批列表出现对应记录；审批通过返回 200；活动流包含审批通过事件

## 回归
- 再次执行审批驳回：`POST /api/approvals/{id}/reject/` JSON: `{"reason":"数据不准确"}`
- 活动流显示“审批驳回 socialmediastats#<id> 数据不准确”

## 结论
- 通过；建议前端新增社媒粉丝列表与录入页面（已创建 `/social/stats`、`/social/stats/create`）。
