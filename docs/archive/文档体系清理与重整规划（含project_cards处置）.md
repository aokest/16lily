## 目标
- 全量梳理本仓库 Markdown 文档与说明文件，建立一个清晰、无重复、可持续维护的文档体系。
- 明确两套目录（16lily 与 project_cards）的作用边界，保留主线、归档历史/原型。
- 所有操作先在“测试环境/备份”中进行，验证无误后再应用到主环境，可随时回滚。

## 范围
- 路径：/16lily/docs、/16lily/.trae/documents、仓库根目录下 AGENTS.md/DEV_NOTES.md、/project_cards/docs 及其相关说明文件。
- 不变更业务代码与运行配置，仅重整文档与说明性文件。

## 风险控制与回滚
- 先做全量备份（Mac 终端可复制）：
  - mkdir -p backups && tar -czf backups/docs_backup_$(date +%F).tar.gz 16lily/docs project_cards/docs .trae/documents AGENTS.md DEV_NOTES.md
- 建立“测试环境”目录用于试整：
  - mkdir -p staging && cp -R 16lily/docs staging/docs && cp -R project_cards/docs staging/project_cards_docs && cp -R .trae/documents staging/trae_docs
- 验证通过后再同步至主环境；若出现问题，解压备份覆盖即可回滚。

## 文档分类与最终目录结构（建议）
- docs/
  - release-notes/ （版本发布说明；例如 ReleaseNotes_v0.9.1.md 按版本归档）
  - handover/ （版本/阶段交接文档；保留按版本的 handover_vX.Y.Z.md，顶层 HANDOVER.md 作为索引）
  - dev_log/ （按日期的开发日志；顶层 DEV_LOG.md 作为目录索引）
  - debug_lessons/ （问题与经验沉淀；顶层 DEBUG_LESSONS.md 作为索引）
  - design/
    - DESIGN_SYSTEM.md（规范）
    - DESIGN_REFACTOR.md（设计重构与决策记录）
  - product/
    - PRODUCT_SPEC.md（产品规格）
    - USER_MANUAL.md（用户使用手册）
  - technical/
    - TECHNICAL_DOCS.md（技术架构与模块说明）
    - DEVELOPMENT.md（开发环境、启动与依赖）
    - STARTUP_CONTEXT.md（早期上下文，建议迁入 technical/archive/）
  - planning/
    - ROADMAP.md（长期路线）
    - PLAN.md（当前迭代计划）
    - STATUS_REPORT.md（阶段/周报）
    - PROJECT_TRACKING.md（任务追踪，若与 Issue/计划重复可并入 PLAN.md 或归档）
  - ai/
    - AI_COLLABORATION_GUIDE.md
    - AI_DIALOGUE_ARCHITECTURE.md
  - archive/ （历史文档、过期说明、一次性计划；用于容纳 .trae/documents 中不再需要长期维护的稿件）

## 重复/冗余处理规则
- 顶层索引 + 子目录明细：保留顶层综述文档（如 HANDOVER.md、DEV_LOG.md、DEBUG_LESSONS.md）作为索引，具体内容放入对应子目录按版本/日期归档。
- 重复内容合并：
  - HANDOVER.md、HANDOVER_20251213.md 与 handover/handover_v0.9.1.md 归并至 handover/ 下，顶层 HANDOVER.md 只保留目录与链接。
  - DEV_LOG.md 只保留“目录与导航”，具体日记保留在 dev_log/ 按日期文件；若 DEV_LOG.md 存在正文重复内容，迁移到对应日期文件并从 DEV_LOG.md 移除。
  - DEBUG_LESSONS.md 作为索引；将具体案例放入 debug_lessons/（如 v0.9.1.md），如存在重复则以“时间最近、内容更完整”的版本为准，旧稿移动到 archive/。
  - DESIGN_REFACTOR.md 中若存在规范性内容，与 DESIGN_SYSTEM.md 重叠的部分迁入 DESIGN_SYSTEM.md，仅在 DESIGN_REFACTOR.md 记录“变更历史与动机”。
  - TECHNICAL_DOCS.md 与 DEVELOPMENT.md：将环境/启动类信息统一放入 DEVELOPMENT.md；架构与模块说明留在 TECHNICAL_DOCS.md，重复部分合并并在两者交叉处加链接。
  - PLAN.md、ROADMAP.md、STATUS_REPORT.md、PROJECT_TRACKING.md：
    - ROADMAP：长期战略；
    - PLAN：当前迭代；
    - STATUS_REPORT：周期汇报；
    - PROJECT_TRACKING：若仅是历史任务列表且与 PLAN 重叠，合并至 PLAN 或归档。
  - ReleaseNotes_vX.Y.Z 与 CHANGELOG.md：版本发布细节保留 release-notes/；CHANGELOG.md 记录摘要并链接到详细版本说明。
- .trae/documents：
  - 将执行过且已沉淀到正式 docs 的稿件迁移到 docs/planning/ 或 docs/archive/。
  - 仍在进行中的“工作计划”留在 .trae/documents 并定期整理到 docs。

## project_cards 目录处置建议
- 角色定位：原型/静态页面与数据转换脚本（如 cardv8.html、project_timeline.html、convert_data.py）；与主线前端（frontend_dashboard）功能高度重叠。
- 建议：
  - 迁移到 legacy/project_cards/（或 docs/archive/project_cards/）作为历史原型保留；
  - 与 16lily 的前端功能（如 StandaloneCardEditor.vue）对照后，将仍有价值的文档/示例迁入 docs 示例区，其余归档。
- 保留最小必要文件：README.md、系统架构与数据模型说明（02-系统架构设计.md、02-数据模型.md）、重要示例；其余按需归档。

## 检测与核验方法
- 目录结构核验：使用 tree/find 查看清理后目录结构是否与规划一致。
- 重复内容快速检索：
  - 标题重复：grep -R "^# " -n docs | sort
  - 近似重复（粗略）：对文件做去标点与小写归一后，用 shasum 比对（示例脚本会提供）。
- 链接有效性：抽样检查 Markdown 内的相对链接是否指向新结构；后续可提供 Python 脚本做批量校验。

## 执行步骤（测试环境 → 主环境）
1. 备份与 staging 构建（见“风险控制与回滚”命令）。
2. 在 staging 中按“文档分类与最终目录结构（建议）”创建目录并移动/合并文件。
3. 运行“检测与核验方法”，确认无遗漏与错误链接。
4. 将 staging 变更应用到主环境（移动文件、删除重复、建立索引型 README/目录文件）；保留 archive/。
5. 更新 CHANGELOG.md，记录“文档重整”这一版本项，并在 ReleaseNotes_v0.9.2.md（建议）中给出改动列表与影响范围。

## 产出物
- 规范化的 docs 目录结构与索引入口。
- 重复/冗余文档的合并版（保留历史归档）。
- project_cards 的处置与保留清单。
- 回滚备份包与可复用的检查脚本（如需要）。

## 后续维护建议
- 每次迭代结束：发布 ReleaseNotes_x，并将变更摘要同步到 CHANGELOG。
- 每周：更新 STATUS_REPORT，必要时更新 PLAN。
- 每月：在 debug_lessons/ 归档一次经验总结，并清理 .trae/documents 中已完成的计划文稿。

请确认以上规划。确认后我将按“测试环境 → 校验 → 主环境”的流程执行，并在关键步骤前后提交核验结果与可复制命令。