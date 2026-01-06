# UI/UX 修复与功能增强方案

根据您的反馈，我将执行以下修复和优化：

## 1. 修复“看不见的按钮” (MainLayout.vue, OpportunityList.vue)
**问题**: 顶部导航栏右侧按钮和“新建商机”按钮因背景色配置问题导致“白字白底”不可见。
**修复方案**:
- 不依赖可能失效的 Tailwind 自定义颜色类（如 `bg-pomegranate-500`）。
- 直接使用 Hex 颜色代码（`bg-[#D64045]`）强制指定背景色，确保按钮在任何环境下都清晰可见。

## 2. 卡片编辑与时间轴“独立窗口化” (CardEditor, Router, ProjectBoard)
**问题**: 模态框在笔记本上显示不全，且受限于主布局。
**修复方案**:
- **改造 CardEditor**: 增加 `mode` 属性，支持“页面模式”渲染（去除黑色遮罩和固定定位）。
- **新建独立页面**: 创建 `StandaloneCardEditor.vue` 和 `StandaloneTimeline.vue` 视图组件。
- **注册路由**: 在 `router/index.ts` 中添加 `/standalone/card/:id` 和 `/standalone/timeline/:projectId` 路由，不使用 MainLayout 布局（全屏显示）。
- **交互更新**: 修改项目看板（ProjectBoard）中点击卡片和“查看推进表”的行为，改为 `window.open()` 打开新标签页。

## 3. 修复通知铃铛 (MainLayout.vue)
**问题**: 铃铛按钮有红点但无法点击。
**修复方案**:
- 为铃铛按钮添加点击事件，弹出一个简单的提示框（Toast/Alert），告知用户“通知中心即将上线”，消除“由于Bug导致无法点击”的误解。

## 下一步
确认后，我将按顺序修改路由配置、创建新视图文件、并更新相关组件代码。