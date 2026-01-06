# 项目开发日志 (DEV LOG)

## 2025-12-30: 解决前端代码更新不生效问题

### 问题描述
在开发卡片编辑器（CardEditor.vue）时，多次修改代码（添加返回按钮、上一张/下一张功能），但在浏览器端始终无法看到界面变化。即使重启 Docker 容器、强制刷新浏览器，问题依旧。

### 根本原因
Docker 容器的文件卷挂载（Volume Mount）存在同步延迟或失效的问题。
虽然宿主机（Host）上的代码文件已更新，但 Docker 容器内的 `/app` 目录下的文件并未实时同步更新。导致 `vite` 服务一直使用的是旧版文件进行热更新或构建。

### 解决方案
采用 **强制覆盖** 策略：
1.  在宿主机修改代码。
2.  使用 `docker cp` 命令强制将修改后的文件复制到容器内：
    ```bash
    docker cp "frontend_dashboard/src/components/CardEditor.vue" opportunity_system-dashboard-1:/app/src/components/CardEditor.vue
    ```
3.  重启容器以触发 Vite 重新加载：
    ```bash
    docker restart opportunity_system-dashboard-1
    ```

### 预防措施
1.  **开发阶段验证**：如果发现界面未更新，第一时间进入容器检查文件内容：
    ```bash
    docker exec <container_id> cat /path/to/file | grep "new_feature_keyword"
    ```
2.  **构建策略**：在进行结构性大改动时，建议使用 `docker-compose up -d --build` 强制重新构建镜像，以确保所有依赖和文件都是最新的。

---

## 2025-12-30: 优化卡片编辑器布局

### 问题
原来的卡片编辑器将工具栏（Toolbar）放置在右侧编辑区域的顶部。这导致：
1.  左侧预览区域没有统一的头部。
2.  "返回"、"上一张"、"下一张" 等全局导航按钮被限制在右侧区域，视觉上不够直观，且容易产生 Z-Index 层级覆盖问题，导致按钮不可点击。

### 修复
重构了 `CardEditor.vue` 的 DOM 结构：
1.  **全局顶部工具栏**：将 Toolbar 移至最外层容器的顶部，横跨整个弹窗宽度。
2.  **分栏布局**：工具栏下方才是左右分栏（左侧预览，右侧编辑）。
3.  **层级优化**：确保工具栏拥有独立的层级上下文，不再受限于右侧栏的 `relative` 定位。

### 结果
- 返回按钮和导航按钮现在位于弹窗的最顶端，清晰可见且易于点击。
- 解决了因层级覆盖导致的按钮“点击无效”问题。

---

## 2025-12-30: 修复AI功能冻结与保存交互问题

### 1. AI 功能冻结 (Freeze)
**问题现象**：
点击“AI 智能优化”按钮后，界面无反应，且所有按钮（包括返回、关闭）失效，仿佛页面卡死。

**原因分析**：
- **前端**：`runAI` 函数在发送请求时设置了 `aiLoading = true`，但缺乏请求超时设置（axios 默认无超时）。
- **后端**：AI 服务（LLM）响应缓慢或挂起时，前端请求一直处于 Pending 状态。
- **状态死锁**：由于请求未返回且未捕获错误，`aiLoading` 状态一直保持为 `true`，导致所有绑定了 `:disabled="aiLoading"` 的按钮（包括关闭按钮）一直处于禁用状态。

**修复方案**：
1.  **增加超时控制**：在 `api.post` 请求中显式添加 `timeout: 60000` (60秒)。
2.  **防御性编程**：在 `finally` 代码块中强制重置 `aiLoading = false`，确保无论成功与否，UI 都能恢复交互。
3.  **提示词优化**：同步 `docs/09-AI提示词.md` 中的最佳实践到后端 `core/views.py`，确保 LLM 输出符合预期的 JSON 格式，减少解析错误。

### 2. 保存后自动退出
**问题现象**：
点击“保存”按钮后，弹窗自动关闭，用户体验不连贯（通常保存后可能还需继续编辑）。

**原因分析**：
`save()` 函数中显式调用了 `emit('update:visible', false)`。

**修复方案**：
移除该行代码，改为仅触发 `save` 事件和重置“未保存状态”标记。

---

## 2026-01-04: 优化项目管理功能与卡片编辑器

### 1. 项目状态与阶段维护优化
**改进点**：
- 更新了 [models.py](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/core/models.py) 中 `Project` 模型的 `Stage` 类，将“回款推进中”标签更新为更准确的“已经回款”，以匹配实际业务流程。
- 同步更新了 [ProjectBoard.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/projects/ProjectBoard.vue) 中的阶段选项，确保前后端一致。

### 2. 卡片编辑器（CardEditor）深度改进
**核心修复**：
- **解决 Prop 直接修改问题**：在 [CardEditor.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/components/CardEditor.vue) 中引入了 `localCardData` 响应式副本。现在，子项目阶段和进度的修改首先作用于本地副本，仅在点击“保存”时才会通过 `emit` 同步到父组件，遵循了 Vue 的单向数据流原则。
- **预览增强**：在卡片预览区域（左侧）增加了子项目阶段标签和进度条显示，用户可以直观地看到当前卡片的执行状态。

### 3. “新增卡片”交互优化
**体验提升**：
- **独立页面打开**：在 [ProjectBoard.vue](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%A9%E7%BB%9F%E8%AE%A1/opportunity_system/frontend_dashboard/src/views/projects/ProjectBoard.vue) 中，点击“新增卡片”现在会直接在独立新窗口中打开编辑器，而不是在侧边栏弹出，提供了更宽阔的编辑视野。
- **防止拦截逻辑**：优化了新窗口打开逻辑，通过先打开空白页再跳转的方式，有效减少了被浏览器广告拦截器误拦截的概率。
- **组件精简**：从项目看板页面移除了不再使用的弹窗式编辑器代码，使页面逻辑更加纯粹，专注于数据展示。

---

## 2026-01-04: 修复本地后端服务崩溃与数据获取失败问题

### 问题描述
用户反馈本地环境（http://127.0.0.1:8080/）出现“获取失败”错误，涉及个人中心、项目管理、用户管理等多个模块。后端服务在启动或处理 API 请求时崩溃。

### 根本原因
代码中存在对已删除或不存在的数据模型（`SocialMediaAdmin` 和 `SocialMediaAdminHistory`）的引用：
1.  **视图层 (Views)**: `core/views.py` 尝试从 `core.models` 导入这些不存在的模型，并包含一个引用它们的私有函数 `_sync_admins`。
2.  **序列化层 (Serializers)**: `core/serializers.py` 中虽然已注释掉相关序列化器，但视图层的导入错误导致整个模块无法加载。
3.  **导入异常 (ImportError)**: 由于 `core.models` 中找不到上述模型，Django 后端抛出 `ImportError`，导致服务启动失败或 API 接口 500 错误。

### 解决方案
1.  **代码清理**:
    -   在 `core/views.py` 中删除了 `SocialMediaAdmin` 和 `SocialMediaAdminHistory` 的所有导入语句。
    -   删除了 `_sync_admins` 内部辅助函数（该函数曾尝试操作不存在的模型）。
    -   清理了 `ResetTestDataView` 中尝试清空这些不存在模型数据的逻辑。
2.  **数据验证**:
    -   通过 Django Shell 验证数据库底层数据完整性。确认 `Opportunity` (5条), `Project` (7条), `Customer` (2条), `User` (11条) 等核心业务数据完好无损。
3.  **配置核查**:
    -   确认 `backend/jazzmin_settings.py` 已将这些不存在的模型加入 `hide_models` 列表，防止后台管理界面因尝试加载它们而报错。

### 结果
-   后端服务恢复正常启动，API 响应恢复。
-   前端各模块（个人中心、商机、项目等）重新获得数据访问权限。
-   确认数据未丢失，系统稳定性得到保障。

---

### 功能更新
1.  **商机状态扩展**
    -   新增 `SUSPENDED` (商机暂停) 和 `TERMINATED` (商机终止) 状态。
    -   前端 `OpportunityList.vue` 增加对应的颜色标识（黄色暂停，红色终止）。
    -   商机列表增加状态和阶段筛选功能。

2.  **业绩报表修复与优化**
    -   **数据丢失修复**：修复 `PerformanceReportView` 查询逻辑，确保包含所有 `ACTIVE` (进行中) 的商机，并排除已中止或完成确收的商机。
    -   **业绩目标管理**：
        -   前端：将目标录入从简单表单重构为表格化输入，支持按月录入新签合同、回款毛利、确认收入。
        -   后端：新增 `bulk_update_targets` 接口，支持批量更新并自动触发分层聚合逻辑（月->季->年，个人->部门）。

3.  **项目管理增强**
    -   **强制绑定规则**：严格执行“项目必须绑定商机”的业务规则。
        -   后端 `ProjectSerializer` 强制校验 `opportunity` 字段。
        -   前端 `ProjectList.vue` 创建弹窗中，商机字段设为必填。
    -   **交互优化**：
        -   完善商机选择逻辑，选择商机后自动填充关联客户信息（支持自动获取详情）。
        -   统一使用 `ElMessage` 组件替代原生 `alert`，提供更友好的操作反馈。

4.  **系统稳定性**
    -   修复了部分页面（如 ProjectList）因导入缺失导致的白屏问题。
    -   清理了部分过时的代码逻辑。

### 下一步计划
-   [ ] **验证**：对项目创建、业绩目标录入进行端到端测试。
-   [ ] **AI分析**：集成新的商机状态到 AI 分析模块，提供针对暂停/终止商机的复盘建议。
-   [ ] **前端优化**：继续优化移动端适配和表格展示性能。
