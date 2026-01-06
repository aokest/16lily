# 🧭 版本更新与交接文档（v0.9.1）

## 版本信息
- 版本号：v0.9.1
- 日期：2025-12-31
- 范围：前端 Dashboard（CardEditor、MainLayout、PersonalCenter）

## 今日完成（变更摘要）
- 卡片编辑器
  - 新增“样式”按钮（可视化调参：正文字号、行距、标题字号、分隔线粗细）
  - 采用 Teleport + 绝对定位，确保菜单不受父容器裁剪与层级影响
  - 右侧“输出物”布局重构：grid-rows-[auto_auto_1fr]，稳定占满剩余空间并与左列底线对齐
- 通知铃铛
  - localStorage 为空时注入默认消息，统一倒序展示最近 10 条
  - 红点状态与列表联动

## 关键代码引用
- 样式菜单与参数绑定（CardEditor）
  - 工具栏及菜单：[CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue#L30-L74)
  - 菜单定位与切换：[CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue#L270-L312)
  - 标题字号与分隔线绑定：[CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue#L90-L99)
  - 全部 Section 的字号与行距绑定（左/右列）：[CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue#L116-L142)
- Section 组件支持动态分隔线与行距（CardSection）
  - 动态 borderBottomWidth、lineHeight：[CardSection.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardSection.vue#L1-L14)
- 通知铃铛默认数据与倒序（MainLayout）
  - localStorage 读取与默认注入：[MainLayout.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/layout/MainLayout.vue#L296-L305)

## 验证与结果
- 手工测试
  - /standalone/card/:id 页面：样式菜单四个滑块全部生效；输出物位置与左列底线对齐；主题与样式互不干扰
  - 顶部铃铛：出现红点；下拉展示最近 10 条；“查看更多通知消息”跳转个人中心正常
- IDE 自检
  - 关键文件无阻断级诊断错误（仅有浏览器 beforeunload 的 returnValue 弃用提示，不影响功能）

## 经验与教训
- 下拉菜单应避免被父容器裁剪：优先使用 Teleport 到 body 并用 getBoundingClientRect 定位
- 复杂嵌套布局需显式高度传递：grid-rows 明确行结构比“单纯 flex-1”更稳定
- 表单与样式参数绑定必须保证数据类型：range 需要 v-model.number，避免字符串导致样式无效

## 工作交接说明
- 编辑器入口
  - 独立页路由：`/standalone/card/:id`（适合全屏编辑与测试）
  - 组件：`frontend_dashboard/src/components/CardEditor.vue`
- 样式菜单
  - 打开：点击工具栏“样式”
  - 定位：Teleoprt 到 body；按钮位置通过 getBoundingClientRect 计算
- 调试与测试建议
  - 若菜单未出现，检查：是否被浏览器扩展阻挡；或 Teleport 未挂载
  - 若“输出物”塌陷，检查祖先 grid 是否 h-full，以及 min-h 是否被覆盖
  - 若滑块不生效，检查 v-model.number 与绑定样式是否连通

## 下一步开发规划
1. 卡片编辑器
   - 样式预设方案管理（保存/加载自定义样式集）
   - 导出静态图片（PNG）与 PPT 模板对接（结合 pptx 技能）
2. 个人中心
   - 将 Mock 数据替换为后端接口（待办、项目列表、消息中心）
   - 增加消息详情页与已读/未读批量操作
3. 报表模块
   - 按部门与个人维度的五项指标聚合 API 对接（Pipeline/合同/回款/毛利/收入）
4. 稳定性与可测试性
   - 引入 webapp-testing 自动化脚本，覆盖样式菜单、分栏布局、通知下拉三大场景

## 版本标记建议（操作参考）
> 仅作为参考命令，不自动执行
```
git tag -a v0.9.1 -m "UI 修复与样式菜单上线：CardEditor Teleport 下拉、输出物布局稳定、通知铃铛默认数据与倒序"
git push origin v0.9.1
```

---
本文档用于记录本次迭代的目标、过程和结果，便于后续接手者快速理解上下文并持续推进。
