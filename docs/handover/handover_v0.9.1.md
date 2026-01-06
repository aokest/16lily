# 🧪 工作交接（v0.9.1）

## 环境与入口
- 前端 Dashboard 根：`opportunity_system/frontend_dashboard`
- 独立卡片编辑器：`/standalone/card/:id`
- 主要组件：
  - 卡片编辑器：`src/components/CardEditor.vue`
  - Section：`src/components/CardSection.vue`
  - 主布局：`src/layout/MainLayout.vue`
  - 个人中心：`src/views/dashboard/PersonalCenter.vue`

## 操作说明
- 样式菜单：工具栏点击“样式”→ 调整四个参数 → 实时生效
- 主题菜单：工具栏点击“主题”→ 选择预设或自定义背景色
- 输出物布局：固定位于右列第三行，随剩余空间自适应
- 通知铃铛：点击查看最近 10 条，支持“全部已读”与“查看更多”

## 常见问题与排查
- 菜单不出现：检查 Teleport 是否挂载、是否被浏览器扩展拦截
- 输出物塌陷：确认祖先容器 h-full / min-h，右列是否为 grid-rows-[auto_auto_1fr]
- 滑块无效：确保使用 `v-model.number`，并检查样式绑定路径是否正确

## 继续开发路线
- 样式预设（保存/加载）
- API 接口对接（待办、项目、消息、报表）
- 自动化测试（webapp-testing 技能），覆盖菜单、布局、通知三大场景

## 文档索引
- 设计系统：[DESIGN_SYSTEM.md](../design/DESIGN_SYSTEM.md)
- 版本说明：[ReleaseNotes_v0.9.1.md](../release-notes/ReleaseNotes_v0.9.1.md)
- 调试经验：[debug_lessons/v0.9.1.md](../debug_lessons/v0.9.1.md)
- 每日日志：[dev_log/2025-12-31.md](../dev_log/2025-12-31.md)
