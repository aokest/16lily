# 🎨 设计系统文档 (Design System)

## 设计目标
- 提升 CRM 前端的统一性、可调性与可测试性
- 保持“石榴粒粒”主题的品牌辨识度（深色红、金色点缀、柔和阴影）

## 设计令牌（Design Tokens）
- 颜色
  - 主色（Pomegranate）：#D64045
  - 点缀（Gold）：#D4AF37
  - 文本（Graphite）：#1F2937
- 字体
  - 中文：Noto Sans SC
  - 英文：Inter / System UI
- 间距与圆角
  - 卡片圆角：8px
  - 组件间距：8px/12px/16px 分层

## 卡片编辑器可视化样式参数
- 正文字号（fontSize，默认 14）
  - 作用域：所有 CardSection 正文
- 正文行距（lineHeight，默认 1.5）
  - 作用域：所有段落的行间距
- 标题字号（titleSize，默认 24）
  - 作用域：卡片左上主标题
- 分隔线粗细（borderWidth，默认 2）
  - 作用域：主标题下分隔线与各 Section 标题下分隔线

参数与代码映射：
- 入口文件：[CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue)
- Section 样式组件：[CardSection.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardSection.vue)

## 主题系统与可见性策略
- 下拉菜单统一使用 Teleport + 绝对定位，避免父容器 overflow 裁剪
- 菜单定位使用 getBoundingClientRect，确保与触发按钮贴合
- 主题切换与样式调参互不干扰（主题负责配色，样式负责排版）

## 布局稳定性规范
- 右列“输出物”采用栅格行结构 grid-rows-[auto_auto_1fr]
  - 前两行为固定高度内容，第三行填充剩余空间
- 祖先容器必须传递高度（h-full / min-h），避免 flex-1 在复杂嵌套中塌陷

## 测试规范（与 webapp-testing 技能结合）
- 场景 1：点击“样式”，断言菜单可见并截图
- 场景 2：调整四个滑块，断言预览出现字号、行距、线宽、标题大小的变化
- 场景 3：输出物与左列底线对齐截图

## 后续拓展
- 样式预设保存/加载（用户个性化）
- 导出 PNG/PPT（与 pptx 技能集成）
- 主题库扩展（十款主题的品牌化适配）

> **版本**: v1.0.0 (初始草案)
> **创建日期**: 2025-12-30
> **说明**: 本文档定义了项目的设计语言、组件规范和样式指南，用于指导 UI/UX 现代化改造。

---

## 1. 设计原则 (Design Principles)

### 1.1 核心原则
- **专业性与现代感**: 体现“网络安全咨询”的专业形象，同时保持科技感与时尚感。
- **一致性**: 全站设计语言统一，避免风格割裂。
- **易用性**: 交互直观，减少认知负担。
- **品牌强化**: 保持“石榴红+金”的品牌识别色，但进行现代化演绎。

### 1.2 视觉基调
- **行业属性**: 网络安全 → 可靠、严谨、科技、前沿。
- **情感基调**: 专业可信中带有温度（避免冷冰冰的工业感）。
- **目标用户**: 企业销售、项目经理、技术顾问。

---

## 2. 设计 Token (Design Tokens)

### 2.1 颜色系统 (Color System)

#### 品牌色 (Brand Colors)
| 名称 | HEX | RGB | 使用场景 |
| :--- | :--- | :--- | :--- |
| **石榴红 (Pomegranate)** | `#D64045` | `214 64 69` | 主要按钮、重要标签、品牌标识 |
| **金色 (Gold)** | `#D4AF37` | `212 175 55` | 强调色、图标、边框装饰 |
| **深红 (Dark Red)** | `#A61B29` | `166 27 41` | 悬停状态、深色模式 |

#### 中性色 (Neutral Colors)
| 名称 | HEX | 使用场景 |
| :--- | :--- | :--- |
| **石墨黑 (Graphite)** | `#1A1A1A` | 标题文字 |
| **深灰 (Dark Gray)** | `#4A4A4A` | 正文文字 |
| **中灰 (Medium Gray)** | `#757575` | 次要文字、图标 |
| **浅灰 (Light Gray)** | `#E5E5E5` | 边框、分隔线 |
| **背景灰 (Background)** | `#F8F9FA` | 页面背景 |

#### 功能色 (Functional Colors)
| 状态 | HEX | 使用场景 |
| :--- | :--- | :--- |
| **成功 (Success)** | `#10B981` | 成功状态、完成标签 |
| **警告 (Warning)** | `#F59E0B` | 警告状态、进行中标签 |
| **错误 (Error)** | `#EF4444` | 错误状态、危险操作 |
| **信息 (Info)** | `#3B82F6` | 信息提示、链接 |

### 2.2 字体系统 (Typography)

#### 字体栈 (Font Stack)
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', monospace;
```

#### 字体缩放 (Type Scale)
| 层级 | 字体大小 | 行高 | 字重 | 使用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **H1** | `2.5rem` (40px) | `1.2` | `900` | 页面主标题 |
| **H2** | `2rem` (32px) | `1.25` | `800` | 区块标题 |
| **H3** | `1.5rem` (24px) | `1.3` | `700` | 卡片标题 |
|H **4** | `1.25rem` (20px) | `1.4` | `600` | 小节标题 |
| **Body Large** | `1.125rem` (18px) | `1.5` | `400` | 大段正文 |
| **Body** | `1rem` (16px) | `1.6` | `400` | 常规正文 |
| **Small** | `0.875rem` (14px) | `1.4` | `400` | 辅助文字、标签 |
| **Caption** | `0.75rem` (12px) | `1.3` | `500` | 说明文字 |

### 2.3 间距系统 (Spacing)

基于 **8px** 基准单位的间距系统：

| 尺寸名称 | 像素值 | 使用场景 |
| :--- | :--- | :--- |
| **xxs** | `4px` | 元素内微小间距 |
| **xs** | `8px` | 图标与文字间距 |
| **sm** | `12px` | 紧凑间距 |
| **md** | `16px` | 常规间距 |
| **lg** | `24px` | 区块间距 |
| **xl** | `32px` | 大区块间距 |
| **2xl** | `48px` | 页面级间距 |

### 2.4 圆角系统 (Border Radius)

| 尺寸 | 值 | 使用场景 |
| :--- | :--- | :--- |
| **none** | `0` | 直角元素 |
| **sm** | `4px` | 小按钮、输入框 |
| **md** | `8px` | 常规按钮、卡片 |
| **lg** | `12px` | 大卡片、容器 |
| **xl** | `16px` | 模态框、侧边栏 |
| **2xl** | `24px` | 特色卡片、头像 |

### 2.5 阴影系统 (Shadow System)

| 层级 | 值 | 使用场景 |
| :--- | :--- | :--- |
| **sm** | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | 轻微悬浮、边框增强 |
| **md** | `0 4px 6px -1px rgb(0 0 0 / 0.1)` | 卡片、按钮悬浮 |
| **lg** | `0 10px 15px -3px rgb(0 0 0 / 0.1)` | 模态框、侧边栏 |
| **xl** | `0 20px 25px -5px rgb(0 0 0 / 0.1)` | 浮层、下拉菜单 |
| **2xl** | `0 25px 50px -12px rgb(0 0 0 / 0.25)` | 特殊强调、大弹窗 |

---

## 3. 组件规范 (Component Specifications)

### 3.1 卡片 (Card)
**设计目标**: 展示项目信息的核心容器，需要兼具信息密度与视觉美感。

**结构**:
```
Card Container
├── Header (标题区)
│   ├── 项目编号 (右上角徽章)
│   └── 项目名称 (主标题)
├── Content (内容区)
│   ├── 左右分栏布局 (7:5)
│   │   ├── 左: 核心信息 (目标、现状、内容)
│   │   └── 右: 辅助信息 (周期、部门、输出物)
│   └── 底部元数据 (预算、状态)
└── 交互状态 (悬停、选中)
```

**样式规范**:
- **容器**: `bg-white`, `rounded-xl`, `shadow-lg`, `border border-gray-100`
- **悬停**: `hover:shadow-xl`, `hover:border-gray-300`, `transition-all duration-200`
- **选中**: `ring-2 ring-blue-500`, `border-blue-500`

### 3.2 按钮 (Button)

**变体**:
| 类型 | 背景色 | 文字色 | 边框 | 使用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **Primary** | `bg-pomegranate` | `text-white` | `border-0` | 主要操作 (保存、提交) |
| **Secondary** | `bg-white` | `text-graphite` | `border border-gray-300` | 次要操作 (取消、返回) |
| **Success** | `bg-green-500` | `text-white` | `border-0` | 成功操作 |
| **Danger** | `bg-red-500` | `text-white` | `border-0` | 危险操作 |
| **Ghost** | `bg-transparent` | `text-gray-700` | `border-0` | 文本按钮 |

**尺寸**:
- **Large**: `px-6 py-3 text-base`
- **Medium**: `px-4 py-2 text-sm` (默认)
- **Small**: `px-3 py-1.5 text-xs`

---

## 4. 布局规范 (Layout Guidelines)

### 4.1 看板视图 (Project Board)
- **网格模式**: 响应式 `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- **列表模式**: 单列，重点信息横向排列
- **间距**: 卡片间距 `gap-6` (网格), `gap-4` (列表)

### 4.2 卡片编辑器 (Card Editor)
- **弹窗尺寸**: `w-[95vw] h-[95vh]`, 最大 `max-w-7xl max-h-[90vh]`
- **布局**: 顶部工具栏 + 左右分栏 (3:5 预览:编辑)
- **响应式**: 小屏时切换为上下堆叠

---

## 5. 待办事项 (Todo Items)

### 5.1 设计系统实施
- [ ] 将设计 Token 转换为 Tailwind CSS 配置变量
- [ ] 创建 Vue 组件库 (Button, Card, Input 等)
- [ ] 编写样式使用示例文档

### 5.2 组件改造优先级
1.  **高**: 项目卡片 (`ProjectBoard.vue` 中的卡片)
2.  **高**: 卡片编辑器 (`CardEditor.vue`)
3.  **中**: 侧边栏 (后台管理系统)
4.  **低**: 全局背景与容器

---

## 6. 设计参考 (Design References)

### 6.1 竞品分析
- **Figma**: 简洁的卡片设计，微妙的阴影层次
- **Notion**: 灵活的布局，一致的圆角系统
- **Linear**: 现代的技术产品美学，清晰的视觉层级

### 6.2 灵感来源
- **网络安全行业**: 深色主题 + 高对比度强调色
- **企业级软件**: 信息密度高但视觉不拥挤
- **现代化设计**: 毛玻璃效果、渐变色、微动画

---

**文档维护**: 每次设计变更后，请更新此文档以确保设计系统的一致性。
