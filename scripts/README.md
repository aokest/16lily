# 文档维护自动化脚本

## 概述

本目录包含用于自动化文档维护的Python脚本，帮助您保持文档项目的健康和一致性。这些脚本特别设计用于在文档目录结构调整后，修复内部链接和检测重复内容。

## 脚本列表

1. **docs_link_fix.py** - 文档内部链接修复工具
2. **docs_duplicate_check.py** - 文档重复内容检测工具
3. **maintain_docs.sh** - 一键维护脚本（需调试）

## 快速开始

### 基本使用指令

每次与AI对话时，您可以使用以下指令让AI自动维护文档：

```
请运行文档维护脚本，检查并修复文档链接，检测重复内容。
```

或者更具体的指令：

```
请执行以下文档维护步骤：
1. 运行文档链接修复（试运行模式）
2. 运行重复内容检测
3. 生成维护报告
```

### 常用命令

AI可以为您执行以下命令：

```bash
# 进入项目目录
cd /Users/aoke/code\ test/商机跟进及业绩统计/opportunity_system

# 1. 检查文档链接（试运行）
python3 scripts/docs_link_fix.py

# 2. 实际修复文档链接
python3 scripts/docs_link_fix.py --apply

# 3. 检测重复文档（快速模式）
python3 scripts/docs_duplicate_check.py --quick

# 4. 检测重复文档并生成报告
python3 scripts/docs_duplicate_check.py --output docs/maintenance_report.md
```

## 详细说明

### docs_link_fix.py

**功能**：
- 扫描所有Markdown文件，检测内部链接
- 根据新的文档目录结构更新链接路径
- 支持试运行和实际应用模式

**参数**：
- `--docs-root`：文档根目录（默认：`./docs`）
- `--apply`：实际应用修复（默认：试运行）
- `--verbose`：显示详细信息

**示例**```：
bash
# 试运行：查看需要修复的链接
python3 scripts/docs_link_fix.py

# 实际修复：应用所有修复
python3 scripts/docs_link_fix.py --apply

# 指定文档目录
python3 scripts/docs_link_fix.py --docs-root ./my_docs
```

### docs_duplicate_check.py

**功能**：
- 计算文件的MD5哈希值，识别完全相同的重复文件
- 使用文本相似度算法检测高度相似的文档
- 生成详细的重复内容报告

**参数**：
- `--docs-root`：文档根目录（默认：`./docs`）
- `--output`：输出报告文件路径（可选）
- `--threshold`：相似度阈值（默认：0.8）
- `--quick`：快速模式（仅检测完全相同的重复）

**示例**：
```bash
# 快速检测完全相同的重复文件
python3 scripts/docs_duplicate_check.py --quick

# 完整检测（包括相似度计算）
python3 scripts/docs_duplicate_check.py

# 生成详细报告
python3 scripts/docs_duplicate_check.py --output docs/duplicate_report.md
```

## 维护流程

### 常规维护

1. **每月一次**：运行链接修复和重复检测
2. **文档结构调整后**：必须运行链接修复
3. **新增大量文档后**：运行重复检测

### AI协作指令

当您需要AI协助维护文档时，只需说：

> "请帮我维护项目文档，检查链接和重复内容。"

AI将自动执行以下步骤：
1. 检查Python环境
2. 运行文档链接修复（试运行）
3. 运行重复内容检测
4. 生成简要报告
5. 提供后续操作建议

### 紧急恢复

如果文档出现链接错误，可以快速恢复：

```bash
# 从备份恢复
tar -xzf backups/docs_backup_*.tar.gz -C ./

# 然后运行链接修复
python3 scripts/docs_link_fix.py --apply
```

## 故障排除

### 常见问题

1. **Python版本问题**：
   ```bash
   python3 --version  # 需要Python 3.6+
   ```

2. **权限问题**：
   ```bash  
   chmod +x scripts/*.py
   ```

3. **脚本运行错误**：
   ```
bash   # 检查语法
   python3 -m py_compile scripts/docs_link_fix.py
   
   # 查看详细错误
   python3 scripts/docs_link_fix.py --verbose
   ```

### 联系支持

如果遇到问题，请向AI提供以下信息：
1. 错误消息的完整内容
2. 您执行的具体命令
3. 操作系统和Python版本

## 版本历史

- **2025-12-31**：初始版本，包含链接修复和重复检测功能
- **2025-12-31**：添加CHANGELOG记录和基本维护脚本

---

## 给AI的提示

作为AI助手，当用户请求文档维护时，请：

1. 首先检查脚本是否存在
2. 运行试运行模式让用户确认
3. 根据用户反馈决定是否应用修复
4. 生成简洁的报告摘要
5. 提供明确的后续步骤

记住：用户是技术小白，需要明确、简单的指令和确认步骤。