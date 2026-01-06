# 🌟 项目启动文档 (Startup Context for AI)

> **目标读者**: 新接手的 AI 助手
> **文档用途**: 帮助你瞬间理解项目上下文，从“陌生人”变为“资深开发者”。

你好！欢迎加入 **团队商机与业绩跟进系统 (Opportunity System)** 开发组。
这是一个基于 **Django + Vue** 的数字化管理平台，旨在帮助销售团队管理商机、赛事和市场活动。

在开始任何工作之前，请**仔细阅读**以下内容。

---

## 1. 项目现状速览 (Snapshot)

*   **阶段**: Phase 3 (AI 深度集成完成，准备进入数据对接与重构阶段)
*   **架构**: 
    *   后端: Django 4.2 + DRF (API) + Jazzmin (后台 UI)
    *   前端: 静态 Vue3 + ECharts (大屏) + Django Templates (后台填单)
    *   AI: 集成 DeepSeek/Ollama，通过 API 实现 Chat-to-Form。
*   **核心痛点**: 
    *   大屏数据仍为 Mock 数据，尚未打通后端。
    *   Django Admin 交互受限（计划在 Phase 4 进行前后端分离重构）。

---

## 2. 你的工作守则 (Protocols)

### 🛡️ 守则一：文档即真理
你不是在写代码，而是在**维护一个系统**。代码只是系统的投影，文档才是系统的灵魂。
*   **Action**: 每次修改代码前，先查阅 `docs/` 下的相关文档。修改后，**必须**同步更新文档。
*   **必读清单**:
    *   `docs/AI_COLLABORATION_GUIDE.md`: **你的行动指南**（包含 Prompt 调优策略）。
    *   `docs/PROJECT_TRACKING.md`: 任务进度与目标。
    *   `docs/TECHNICAL_DOCS.md`: 架构与 API 规范。

### 🛡️ 守则二：以终为始
不要为了写代码而写代码。
*   **Action**: 接到任务时，先问自己：“这符合 `ROADMAP.md` 里的规划吗？”
*   如果不符合，请向用户指出，并建议更新 Roadmap。

### 🛡️ 守则三：保持上下文整洁
*   **Action**: 任务完成后，提示用户：“任务已完成，文档已更新。建议 Clear Context 以便开启新任务。”

---

## 3. 项目进化史 (Project Evolution)

了解历史，才能更好地创造未来。以下是我们从立项到现在的演进历程：

1.  **混沌初开 (Phase 1)**:
    *   我们搭建了 Django + Docker 的基础环境。
    *   确立了以 `Opportunity` 为核心的数据模型。
2.  **美化与交互 (Phase 2)**:
    *   引入 `Jazzmin` 替代原生 Admin，定制了“石榴红+金”的企业级主题。
    *   尝试通过 `signals.py` 实现 AI 解析，但发现用户体验极差（无法实时反馈）。
3.  **AI 的阵痛与重生 (Phase 3)**:
    *   **架构转型**: 废弃 Signal 方案，转向 `Chat-to-Form`（前端对话 -> API -> 自动填单）。
    *   **连接之痛**: 遭遇 Docker 容器无法访问宿主机 Ollama 的问题，最终通过 `host.docker.internal` 和自动降级策略解决。
    *   **解析之难**: 本地小模型 (Qwen3:8b) 频繁输出 Markdown 废话，导致 JSON 解析失败。我们通过 **One-Shot Prompt (单样本提示)** 和 **鲁棒的清洗代码** 彻底解决了这个问题。
4.  **文档驱动时代 (Current)**:
    *   随着复杂度上升，我们确立了 **文档驱动开发 (DDD)** 的工作流，确保 AI 即使“失忆”也能通过文档找回状态。

---

## 4. 历史经验教训 (Lessons Learned)

我们走过一些弯路，请不要重蹈覆辙：

1.  **Ollama 解析问题**: 
    *   *现象*: 小模型 (Qwen3:8b) 返回的 JSON 经常包含 Markdown 标记或废话。
    *   *解法*: 我们在 `ai_service.py` 中写了极其健壮的清洗逻辑，并在 Prompt 中使用了 One-Shot (单样本) 示例。**不要轻易改动 Prompt 的结构，除非你确定新模型更聪明。**
2.  **Docker 网络**:
    *   *现象*: 容器内连不上宿主机的 Ollama。
    *   *解法*: 使用 `host.docker.internal`，并确保 Ollama 监听 `0.0.0.0`。
3.  **文档碎片化**:
    *   *现象*: 曾有多个重复的 TODO 文档导致信息不同步。
    *   *解法*: 我们已删除了 `TODO_LIST.md`，统一收敛至 `PROJECT_TRACKING.md`。**请勿创建新的临时计划文档。**   

---

## 5. 如何开始你的第一个任务？

1.  **读取**: 阅读 `docs/PROJECT_TRACKING.md` 中的 "Next Steps"。
2.  **确认**: 询问用户：“根据计划，我们下一步是[任务X]，是否现在开始？”
3.  **执行**: 遵循 `docs/AI_COLLABORATION_GUIDE.md` 中的步骤。

**Trust the docs, trust the process.** 祝你开发顺利！
