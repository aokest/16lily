# UI 修复与优化方案

根据您的反馈，我将执行以下 3 项具体修复：

## 1. 卡片编辑器优化 (CardEditor.vue)
**问题**: 标题过大挤压内容，底部被截断，主题按钮不可见。
**修复方案**:
- **缩小字号与间距**: 将标题 `text-6xl` 降为 `text-4xl`，项目编号 `text-4xl` 降为 `text-2xl`，整体内边距 `p-12` 降为 `p-8`。
- **调整容器高度限制**: 在 `calculateScale` 中，确保内容高度不会无限撑开，而是被 `scale` 包含在可视区域内，或者优化内部 Grid 布局（如 `gap-10` -> `gap-6`）以节省垂直空间。
- **修复主题按钮**: 检查 CSS `z-index` 和 `overflow` 属性，确保下拉菜单不被父容器遮挡。主题按钮已在代码中，可能因颜色或层级问题未显示。

## 2. 个人中心待办事项修复 (PersonalCenter.vue)
**问题**: “待审批” Tab 标签文字紧贴左侧。
**修复方案**:
- **调整 CSS**: 针对 `el-tabs__item` 或 `el-tabs__nav-scroll` 添加 `padding-left: 0` 或调整容器的 `padding`，确保 Tab 文字与下方列表内容对齐。
- **增加内边距**: 给 Tab 头部容器增加 `px-4`。

## 3. 业绩报表重构 (Performance.vue)
**问题**: 需要展示“部门整体”与“个人”的对比数据。
**修复方案**:
- **布局重构**: 移除旧的 Dashboard 布局，改为上下两栏结构。
    - **上栏**: 部门整体业绩 (Department Performance) - 5个指标卡片
    - **下栏**: 个人业绩 (Personal Performance) - 5个指标卡片
- **指标项**: 商机池、新签合同、回款、毛利、确认收入。
- **Mock 数据**: 更新 `fetchData` 逻辑，生成两组 Mock 数据（`departmentStats` 和 `personalStats`）以展示效果。

## 下一步
确认后，我将按顺序修改代码。建议优先修复卡片编辑器，因为这是您当前关注的重点。