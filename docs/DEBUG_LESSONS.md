# 🐛 调试经验与教训知识库 (Debug Lessons Learned)

> **创建日期**: 2025-12-30
> **最后更新**: 2025-12-30
> **说明**: 本文档汇总了项目开发过程中遇到的关键技术陷阱、调试过程及解决方案，旨在为后续开发者提供“避坑指南”。

---

## 2026-01-06 调试记录与修复摘要

### AI 润色功能失效 (404 Error)
**原因**  
- 前端请求地址为 `ai/analysis/`，而后端路由定义为 `ai/analyze/`。

**修改思路**  
- 统一前后端 API 路径为 `ai/analyze/`。
- 优化交互逻辑：点击润色后直接在当前编辑器内更新内容，不再自动保存并退出，提升编辑连续性。

**代码位置**  
- [frontend_dashboard/src/views/daily_reports/DailyReportList.vue:polishReport](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/daily_reports/DailyReportList.vue#L585-L612)

**测试方法**  
1. 前端：点击“AI 润色”，文字应在编辑器内直接变换，且右下角提示“AI 润色完成”。
2. 验证：点击后编辑器不应关闭。

---

### 业绩目标管理：保存成功但列表不刷新/显示混乱
**原因**  
- **过滤逻辑偏差**：前端季度设为 0 表示全年，请求时不传 `quarter` 参数，导致后端返回数据过滤不精准。
- **树形构建逻辑漏洞**：在构建部门-季度-月度的树形结构时，对 `user` 字段的比较（对象 vs ID）不严谨，导致月度数据无法挂载到父节点。

**修改思路**  
- 统一 `user_id` 获取逻辑，兼容对象和 ID 格式。
- 增强树形挂载的鲁棒性：若月度目标找不到对应的季度父节点，则尝试挂载到年度节点或作为独立节点展示。
- 优化保存后的数据重新拉取 (`fetchData`) 流程。

**代码位置**  
- [frontend_dashboard/src/views/reports/PerformanceTargets.vue:fetchData](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/reports/PerformanceTargets.vue)

**测试方法**  
1. 前端：新增一个 2026 年的月度业绩目标，点击保存。
2. 验证：列表应自动刷新，且新目标正确出现在对应部门及人员的树形节点下。

---

### 数据管理界面布局错乱与 Vite 编译错误
**原因**  
- `DataManagement.vue` 中存在重复的 `<script setup>` 标签。
- 使用了未导出的图标组件 `History`（应为 `Clock`）。
- 布局采用旧式的居中对齐，在多卡片场景下显得拥挤且不对齐。

**修改思路**  
- 合并重复的脚本块。
- 替换为 Lucide 标准图标。
- 引入 `el-row/el-col` 响应式栅格系统，重构为卡片流式布局。

**代码位置**  
- [frontend_dashboard/src/views/settings/DataManagement.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/settings/DataManagement.vue)

---

## 2026-01-05 调试记录与修复摘要

### 项目卡片编辑保存失败
**原因**  
- 视图层未显式触发模型的 `save()`，导致 `ProjectCard.save()` 中的子阶段变更日志逻辑未执行。

**修改思路**  
- 在 `ProjectCardViewSet.perform_update()` 中显式调用 `serializer.save()`，以确保模型层日志逻辑生效。

**代码位置**  
- [core/views.py:ProjectCardViewSet.perform_update](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L619-L622)

**测试方法**  
1. 后端：PATCH `/project-cards/{id}/`，修改 `sub_stage` 字段。  
2. 验证：查询 `/projects/{id}/` 的 `change_logs` 是否新增对应记录。

---

### AI 生成/润色功能不可用
**原因**  
- AI 服务返回值为字符串；视图层 `DailyReportViewSet.polish` 仅接受字典（`{'content': ...}`），导致判断失败。

**修改思路**  
- 兼容字符串与字典两种返回值；若为字符串则直接作为润色结果保存。

**代码位置**  
- [core/views.py:DailyReportViewSet.polish](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L632-L656)

**测试方法**  
1. 前端：在“日报”页面新建/编辑后点击“AI 润色”。  
2. 后端：POST `/daily-reports/{id}/polish/`，检查返回的 `polished_content` 是否存在。

---

### 业绩报表数据为 0 或结构不匹配
**原因**  
- 后端接口返回键不符合前端 `Performance.vue` 期望（缺少 `pipeline/signed/groups/monthly` 等）。

**修改思路**  
- 统一接口返回结构：补齐 `totals`、`targets`、`status_distribution`、`groups`、`monthly`。

**代码位置**  
- [core/views.py:PerformanceReportView.get](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L425-L488)

**测试方法**  
1. 前端：报表页刷新，数据不再为 0。  
2. 后端：GET `/reports/performance/?group_by=department&time_range=month&year=2026&month=01` 校验返回结构。

---

### 联系人新建/编辑成功但删除失败
**原因**  
- 删除备份 `original_data` 使用了不存在字段 `position`（模型为 `title`），恢复时报错。

**修改思路**  
- 备份时写入 `title` 字段；保持管理员恢复兼容。

**代码位置**  
- [core/views.py:ContactViewSet.perform_destroy](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L217-L231)

**测试方法**  
1. 前端：删除联系人；  
2. 后端：POST `/contacts/restore/` 恢复，确认恢复成功。

---

### 社媒账号保存失败
**原因**  
- 前端使用 `account_username` 字段，而后端模型字段为 `account_name`；序列化器拒绝未知字段。
- 同时在创建初始统计数据时错误传入了不存在的 `platform` 字段。

**修改思路**  
- 在序列化器中兼容别名字段 `account_username` 并映射到 `account_name`；忽略 `display_name` 等非持久化字段。  
- 创建 `SocialMediaStats` 时移除 `platform` 参数。

**代码位置**  
- [core/serializers.py:SocialMediaAccountSerializer](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/serializers.py#L279-L296)  
- [core/views.py:SocialMediaAccountViewSet.perform_create/update](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L288-L316)

**测试方法**  
1. 前端：新建/编辑社媒账号，点击保存无报错。  
2. 若设置初始粉丝数，应新增一条 `social-stats` 记录。

---

### 项目新建失败
**原因**  
- `ProjectSerializer` 将 `code` 字段设置为只读，导致创建时无法提交必填编号。

**修改思路**  
- 移除 `code` 的只读限制，允许创建时写入项目编号。

**代码位置**  
- [core/serializers.py:ProjectSerializer.Meta.read_only_fields](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/serializers.py#L415-L424)

**测试方法**  
1. 前端：在“项目列表”中点击“新建项目”，填写 `code` 后保存；  
2. 后端：POST `/projects/` 返回 201，列表出现新项目。

---

### 商机新建/编辑保存未知错误
**原因**  
- 前端提交了后端未定义的扩展字段（如 `expected_sign_date`、`win_rate` 等），序列化器拒绝未知字段。

**修改思路**  
- 为序列化器添加这些扩展字段的 `write_only` 兼容，并在 `to_internal_value` 中将 `customer_name` 映射为 `customer_company`。

**代码位置**  
- [core/serializers.py:OpportunitySerializer](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/serializers.py#L297-L330)

**测试方法**  
1. 前端：新建或编辑商机，携带扩展字段保存；  
2. 后端：POST/PATCH `/opportunities/` 返回成功，并可在商机详情中查看保存结果（扩展字段不持久化但不再报错）。

---

### 联系人管理修复 (2026-01-05)
**状态**: ✅ 已修复
**内容**: 
- 恢复了联系人列表缺失的“删除”按钮。
- 修复了后端 `perform_destroy` 逻辑中字段名不匹配的问题。

### 客户管理增强 (2026-01-05)
**状态**: ✅ 已修复
**内容**: 
- 验证并修复了新建客户和编辑客户信息的保存功能，确保所有必填字段和扩展字段正确持久化。

### 审批功能修复 (2026-01-05)
**状态**: ✅ 已修复
**内容**: 
- 修复了审批流程中的逻辑中断问题，确保审批状态流转和日志记录正常工作。

### 项目管理基础功能 (2026-01-05)
**状态**: ✅ 已修复
**内容**: 
- 验证了新建项目和修改项目基本信息的功能，解决了 `code` 字段只读导致的创建失败问题。

---

### CRM 与项目管理核心功能修复 (2026-01-05 经验沉淀)
**状态**: ✅ 已验证

1. **联系人管理**: 修复了联系人列表缺失“删除”按钮的问题，并修正了后端 `perform_destroy` 中的字段引用错误（`position` -> `title`）。
2. **客户信息管理**: 验证并修复了新建客户和编辑客户信息时的保存逻辑，确保所有必填字段（如名称、所属行业等）能正确持久化。
3. **审批流程**: 修复了个人中心审批申请列表无法显示的问题，通过补全 `DepartmentModel` 接口及优化 `ApprovalRequestSerializer` 显示字段（如 `applicant_name`），确保审批流闭环。
4. **项目基本信息**: 解决了新建项目和修改项目基本信息时，因 `code` 字段只读导致的保存失败问题，并优化了项目卡片子阶段变更的自动日志记录。

---

### 业绩目标批量更新 500 错误与数据不一致
**原因**  
- 后端 `bulk_update_targets` 仅更新了单月目标，未同步更新对应的季度和年度汇总，导致报表数据冲突。
- 在个人目标更新时，未自动汇总到所属部门。
- 信号处理函数中对 `creator` 或 `sales_manager` 的访问未做安全检查，导致某些空字段对象保存时触发 Server Crash。

**修改思路**  
- 在 `bulk_update_targets` 中引入自动汇总逻辑：
  1. **维度聚合**：个人 -> 部门。
  2. **时间聚合**：月度 -> 季度 -> 年度。
- 使用 `getattr(instance, 'field', None)` 安全访问模型关联字段。

**代码位置**  
- [core/views.py:PerformanceTargetViewSet.bulk_update_targets](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L208-L370)
- [core/signals.py:auto_create_opportunity_log](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/signals.py#L101-L124)

**测试方法**  
1. 后端：调用 `bulk_update_targets` 更新某人 1 月份目标。
2. 验证：数据库中该月份的部门目标，以及该人/该部门的第 1 季度和年度目标是否同步更新。

---

### 通知消息发布失败
**原因**  
- 后端 `NotificationViewSet` 仅支持读取与标记已读，缺少创建发布接口；前端调用 `POST /notifications/` 失败。

**修改思路**  
- 实现 `create` 方法支持全体、指定部门、指定用户广播；类型支持 `normal/system`。

**代码位置**  
- [core/views.py:NotificationViewSet.create](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L658-L706)

**测试方法**  
1. 前端：个人中心发布消息；  
2. 后端：POST `/notifications/` 返回 `created` 数量，列表显示新消息。

---
### 工作日志 AI 润色内容同步问题
**原因**  
- 编辑工作日志时，表单初始化逻辑优先加载原始内容 (`raw_content`)，导致即使日志已被 AI 润色并保存，再次编辑时仍显示原始未润色文本。

**修改思路**  
- 优化前端 `startEditing` 逻辑：若存在 `polished_content` 且不为空，则优先将其加载到编辑框；否则加载 `raw_content`。

**代码位置**  
- [DailyReportList.vue:startEditing](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/daily_reports/DailyReportList.vue)

**测试方法**  
1. 润色一篇日报并保存。
2. 点击“编辑”按钮，确认文本框内显示的是润色后的内容。

---

### 业绩目标管理：部门显示与保存失败
**原因**  
- 部门字段在前端错误地显示为 ID 数字而非名称。
- 保存时前端提交了硬编码的部门名称字符串，而模型期望的是部门关联 ID。
- `PerformanceTarget` 模型缺少 `target_gross_profit` 和 `target_revenue` 字段。

**修改思路**  
- 前端引入动态部门列表加载，将显示逻辑从 ID 映射为名称。
- 提交保存时，根据选择的部门名称查找对应的动态 ID 进行关联。
- 后端模型补齐缺失字段并运行迁移。

**代码位置**  
- [PerformanceTargets.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/reports/PerformanceTargets.vue)
- [models.py:PerformanceTarget](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/models.py)

**测试方法**  
1. 进入“业绩目标管理”，确认部门显示为“技术部”、“销售部”等名称。
2. 编辑或新增目标，确认保存成功且数据持久化。

---

### 系统日志管理功能实现
**需求**  
- 管理员需要监控系统内的用户登录、数据增删改行为，并支持多维筛选与全量导出。

**实现方案**  
- **后端**: 扩展 `ActivityLog` 模型，增加 `department` 冗余字段；利用 Django Signals 自动捕获核心业务对象（商机、客户、项目、日报等）的生命周期事件。
- **前端**: 新增 `SystemLogs.vue` 界面，支持按类型、部门、操作人、时间范围筛选，并调用后端 CSV 接口进行全量数据导出。

**关键组件**  
- [ActivityLogViewSet](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py)
- [SystemLogs.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/settings/SystemLogs.vue)
- [signals.py](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/signals.py)

---

## 1. Docker 与环境问题

### 🔴 陷阱：宿主机代码修改未同步到容器
**症状**:
- 在 IDE 中修改了前端 Vue 组件或后端 Python 代码。
- 刷新浏览器或重启服务，界面/逻辑始终没有任何变化。
- 甚至删除了文件，服务依然正常运行。

**根本原因**:
- Docker Compose 的 Volume 挂载在某些文件系统（如 MacOS 的 Docker Desktop）或特定配置下存在延迟或失效。
- 或者容器启动时使用了旧的镜像层，而挂载路径配置错误（如相对路径层级不对），导致容器读取的是构建时的 `/app` 目录，而非宿主机的实时挂载目录。

**解决方案**:
1.  **临时救火**: 使用 `docker cp` 强制覆盖容器内文件：
    ```bash
    # 必须在项目根目录执行，且路径要准确
    docker cp opportunity_system/frontend_dashboard/src/components/CardEditor.vue opportunity_system-dashboard-1:/app/src/components/CardEditor.vue
    docker restart opportunity_system-dashboard-1
    ```
2.  **验证方法**: 进入容器检查文件内容：
    ```bash
    docker exec <container_id> cat /app/path/to/file | grep "unique_string"
    ```
3.  **彻底修复**: 检查 `docker-compose.yml` 中的 `volumes` 映射路径是否正确（绝对路径 vs 相对路径）。

### 🟠 陷阱：数据库连接拒绝
**症状**: 
- Django 报错 `psycopg2.OperationalError: could not connect to server: Connection refused`。
- 本地工具（如 Navicat）无法连接数据库。

**原因 & 解决**:
- **内部通信**: 容器间通信必须使用 Service Name (如 `db`) 而非 `localhost` 或 `127.0.0.1`。
- **外部访问**: 默认 `docker-compose.yml` 可能未映射 `5432` 端口到宿主机（出于安全考虑）。如需连接，需在 `ports` 中添加 `"5432:5432"`。

---

## 2. 前端交互与 UI (Vue 3 + Tailwind)

### 🔴 陷阱：Lucide 图标动态渲染失效
**症状**:
- 使用 `lucide.createIcons()` 渲染图标。
- 当 Vue 通过 `v-if/v-else` 切换状态（如 `loading` -> `done`）时，图标消失，只剩下空的 `<i>` 标签。

**根本原因**:
- `lucide.createIcons()` 依赖对 DOM 的一次性扫描。当 Vue 响应式更新 DOM 后，Lucide 并不知道节点变了，不会自动重新注入 SVG。
- 虽然可以使用 `nextTick` 重新调用，但在高频切换或复杂组件中极不稳定。

**最佳实践**:
- **弃用动态 JS 渲染**。
- **直接嵌入 SVG**: 将 SVG 代码直接写在 Vue 模板中，利用 Vue 的响应式能力控制显隐。
  ```html
  <svg v-if="loading" class="animate-spin ...">...</svg>
  <svg v-else ...>...</svg>
  ```

### 🟠 陷阱：Z-Index 层级遮挡
**症状**:
- 按钮看得到但点不动（点击无反应）。
- 鼠标悬停没有手型（Cursor pointer）。

**原因**:
- 父容器设置了 `overflow: hidden` 或较低的 `z-index`。
- 绝对定位（Absolute）元素的层级上下文（Stacking Context）混乱。

**解决**:
- 显式给悬浮层（如 Toolbar, Modal）设置极高的 `z-index` (如 `z-50`, `z-[60]`)。
- 确保按钮显式添加 `cursor-pointer` 类，方便通过视觉排查交互区域。

### 🟡 陷阱：Vue Watchers 数据不同步
**症状**:
- 切换卡片（上一张/下一张），内容未更新。
- 左侧预览区未随右侧输入实时变化。

**解决**:
- **监听 ID 变化**: 必须监听 `props.cardData.id` 而不仅仅是 `visible`。
  ```typescript
  watch([() => props.visible, () => props.cardData?.id], ...)
  ```
- **监听原始文本**: 对于编辑器类组件，需监听 `rawText` 并触发解析逻辑。

---

## 3. AI 业务集成 (LLM Integration)

### 🔴 陷阱：前端界面“假死”
**症状**:
- 点击“AI 优化”后，按钮一直转圈，无法取消，无法关闭弹窗。
- 整个页面似乎卡住了。

**原因**:
- 后端请求耗时过长（LLM 响应慢）。
- 前端 `axios` 请求未设置超时时间（默认为无限等待）。
- 缺乏 `try...catch...finally` 块，导致报错后 `loading` 状态无法重置。

**最佳实践**:
- **设置超时**: `timeout: 30000` (30秒)。
- **强制重置**: 无论成功失败，必须在 `finally` 中将 `loading = false`。
  ```typescript
  try {
      await api.post(..., { timeout: 30000 });
  } finally {
      loading.value = false; // 兜底保障
  }
  ```

### 🔵 经验：提示词工程 (Prompt Engineering)
**问题**: AI 生成的内容像“白开水”，缺乏专业度。
**优化**:
- **角色设定 (Persona)**: 从“项目经理”升级为“资深安全顾问”。
- **术语植入**: 强制要求使用行业黑话（如“态势感知”、“闭环”）。
- **价值导向**: 提示词中强调“解决什么风险”而非“做什么任务”。
- **结构化**: 要求输出 JSON 格式，便于程序解析。

---

## 4. 后端与部署 (Django)

### 🟡 陷阱：静态文件 404
**症状**:
- 部署后样式丢失，Admin 界面丑陋。
- 控制台报 `GET /static/... 404`。

**原因**:
- 生产模式下 (`DEBUG=False`)，Django 不再负责托管静态文件。
- Nginx 未正确配置 `/static/` 别名。

**解决**:
- 运行 `python manage.py collectstatic` 将文件收集到统一目录。
- 确保 Nginx 配置中有 `location /static/ { alias /app/static/; }`。

### 🟡 陷阱：数据库迁移冲突
**症状**:
- 修改了 `models.py` 但报错 `relation does not exist`。

**解决**:
- 严格遵循：修改 Model -> `makemigrations` -> `migrate`。
- 如果开发环境数据混乱，可尝试删除 `migrations/` 下除 `__init__.py` 外的文件及数据库表，重新初始化（仅限开发环境！）。
