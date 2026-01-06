# UI/UX 现代化改造计划 (Frontend Dashboard)

## 🎯 核心目标
根据用户指示，放弃对 Django Admin 的美化，全力聚焦于 **Frontend Dashboard (`http://127.0.0.1:8000/crm`)** 的现代化改造。
利用 `frontend-design` 和 `theme-factory` 技能的指导，将“石榴粒粒”主题（石榴红+金）以现代化的方式应用到 Vue 项目中。

## 🔧 技能应用策略

### 1. **`theme-factory` (主题工厂)**
- **指导原则**: 使用“石榴粒粒”主题（Pomegranate & Gold），但在 Vue 中使用 Tailwind CSS 变量进行现代化演绎。
- **配色方案**:
    - 主色: `pomegranate-500` (#D64045)
    - 辅助色: `gold-400` (#D4AF37)
    - 背景色: `slate-50` -> `gray-50` (更温暖的灰)
    - 侧边栏: 深色渐变 (参考 Django Admin 的改造思路，但用 Tailwind 实现)

### 2. **`frontend-design` (前端设计)**
- **指导原则**: 避免“AI生成的廉价感”，追求专业、高对比度、清晰的层级。
- **布局改造**:
    - **Sidebar**: 摒弃 Element Plus 默认样式，手写 Tailwind 侧边栏。支持折叠、Logo 区域渐变、菜单项悬停微交互。
    - **Main Content**: 增加顶部面包屑、页面标题区域的视觉权重。
    - **Card/List**: 使用 `ProjectBoard` 已验证的卡片样式作为全站标准。

## 📋 详细执行步骤

### 阶段一：布局重构 (`MainLayout.vue`)
1.  **侧边栏现代化**:
    - 移除 `<el-menu>` 的默认样式依赖，改用 Tailwind 自定义菜单组件。
    - 实现“深色模式”侧边栏：背景使用 `bg-slate-900` 或深红渐变，文字使用白色/金色。
    - 添加 Logo 区域：使用品牌色渐变背景 + 金色底边。
    - 菜单项：悬停时显示左侧金色光标，背景轻微变亮。
2.  **顶部导航栏优化**:
    - 增加阴影 (`shadow-sm`)。
    - 优化“战报大屏”和“CRM首页”按钮的样式（使用 Ghost 或 Outline 风格，减少视觉干扰）。

### 阶段二：CRM 核心页面美化
3.  **商机列表页 (`OpportunityList.vue`)**:
    - 将 Element Plus 表格封装在圆角卡片中 (`rounded-2xl shadow-card`)。
    - 优化表格表头：使用浅灰色背景，加粗字体。
    - 状态标签：使用 Tailwind 的 `badge` 样式（圆角、柔和背景色）。
4.  **详情页/表单页**:
    - 使用左右分栏布局（左侧核心信息，右侧时间轴/日志）。
    - 标题区域增强：显示巨大的商机金额和状态徽章。

### 阶段三：Tailwind 配置完善
5.  **确认配置**:
    - 确保之前更新的 `tailwind.config.js` 中的颜色变量（pomegranate, gold）在 Vue 组件中能正确生效。
    - 补充 `safelist` (如果需要动态类名)。

## 🚀 立即执行动作
1.  **重写 `MainLayout.vue`**: 将其从 Element Plus Menu 改造为 Tailwind CSS 布局。
2.  **验证**: 确保 CRM 首页加载正常，侧边栏交互流畅。

请确认此计划是否符合您“废弃 Admin，拥抱 CRM”的战略方向？