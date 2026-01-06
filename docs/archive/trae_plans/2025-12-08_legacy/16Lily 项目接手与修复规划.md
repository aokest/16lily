# 🤖 16Lily (石榴粒粒) 项目接手规划

你好！我已经详细查阅了 `AI_COLLABORATION_GUIDE.md`、`PROJECT_TRACKING.md`、`HANDOVER.md` 和 `ROADMAP.md`。完全理解了项目的背景、目标和当前的紧急任务。

## 📊 项目现状概览

*   **项目定位**: 数字化商机管理与业绩统计指挥中心。
*   **当前阶段**: Phase 3 (AI 深度集成与前端重构)。
*   **技术栈**: Django REST (Backend) + Vue 3 (Frontend) + Docker (目前推荐本地运行)。
*   **核心痛点**: **DeepSeek AI 解析不稳定**（返回 Markdown 而非 JSON），导致智能填单功能经常需要兜底。

---

## 🛠️ 我的行动规划 (Action Plan)

根据 `HANDOVER.md` 的明确指令，我制定了以下分步计划，优先解决“AI 解析失败”这一核心阻碍：

### 🚨 第一优先级：修复 DeepSeek 解析与增强可观测性

目前的盲点在于**不知道 DeepSeek 到底返回了什么**导致解析失败。

1.  **建立“黑匣子”日志 (SubmissionLog)**:
    *   修改 `core/models.py` 和 `ai_service.py`。
    *   在数据库中完整记录：`Prompt` (输入)、`Raw Response` (原始返回)、`Cleaned JSON` (清洗后)、`Error` (报错信息)。
    *   **目的**: 彻底看清 DeepSeek 为什么不听话，是返回了 Markdown 代码块？还是多余的解释文字？

2.  **实施“强约束”策略**:
    *   优化 `ai_service.py` 中的 `_get_llm_response`。
    *   针对 DeepSeek/OpenAI 兼容接口，强制尝试 `response_format={"type": "json_object"}`（如果 Provider 支持）。
    *   增强 Regex 清洗逻辑：专门提取 ````json ... ```` 或 `{ ... }` 块，丢弃所有解释性文字。

3.  **Admin 健康检查工具**:
    *   在 Django Admin 增加“AI 解析自测”按钮，一键测试当前模型配置是否连通且能返回正确 JSON。

### 🎨 第二优先级：UI 与交互修复

1.  **模型下拉菜单优化**:
    *   修改 `ChatWindow.vue`。
    *   锁定宽度为 **320px**，并确保在移动端或窄屏下响应式调整，不挤压右侧按钮。

2.  **前端智能兜底 (Smart Fallback)**:
    *   完善 `ChatWindow.vue` 的兜底逻辑。
    *   当 AI 解析失败但后端 Regex 成功提取了关键词（如“客户名”、“活动类型”）时，**自动填充**到下方的表单中，并显示“已自动提取关键词”提示。

### 🚀 第三优先级：业务功能推进 (按需)

1.  **活动流 (Activity Feed)**:
    *   在 `ActivityLog` 中区分“审批驳回”事件，并在前端用红色高亮显示驳回原因与责任人。
2.  **社媒审批**:
    *   实现社媒粉丝数据的录入与审批流打通。

---

## 💡 立即执行建议

我建议从 **“第一优先级：修复 DeepSeek 解析”** 开始。

如果不解决“看不见原始报错”的问题，我们只能盲目猜测。一旦有了日志，我就能针对性地调整 Prompt 或清洗逻辑，彻底根治这个问题。

**请确认：是否同意我先着手实施 `SubmissionLog` 日志记录与 AI 解析逻辑的优化？**