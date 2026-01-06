# 测试目录说明 (Tests)

目标：规范每次功能开发后的验证流程，沉淀可复用的测试用例与报告。

## 目录结构
- `reports/`：每次测试的报告与结论
- `pocs/`：可执行的测试脚本/命令集合（优先使用 `manage.py` 命令 或 `curl` ）
- `templates/`：测试报告模板

## 执行规范
1. 每次功能开发完成后，产出一份报告到 `reports/`，命名规则：`YYYY-MM-DD-<topic>.md`
2. 报告包含：测试方法、用例/POC、预期、实际、修正、回归结果。
3. 若涉及后端脚本，统一放在 `core/management/commands/`，并在报告中给出执行命令。

参考：`reports/2025-12-10-approvals.md`

