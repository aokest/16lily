"""
接口复现脚本批量运行器

用途:
- 一键运行 8 个复现脚本，生成简要结果汇总，便于定位与回归。

执行方式:
- 在宿主机运行: `python opportunity_system/tests/pocs/run_all.py`

输出:
- 终端打印每个用例的状态摘要
"""

import importlib
import runpy
import os

TEST_FILES = [
    "tests/pocs/test_project_create.py",
    "tests/pocs/test_project_card_update.py",
    "tests/pocs/test_daily_report_polish.py",
    "tests/pocs/test_performance_report.py",
    "tests/pocs/test_contact_delete_restore.py",
    "tests/pocs/test_social_account_save.py",
    "tests/pocs/test_opportunity_create.py",
    "tests/pocs/test_targets_bulk_update.py",
]


def main():
    """
    逐个执行每个复现脚本：
    - 通过 runpy.run_path 运行目标文件，并调用其中的 run() 函数。
    - 避免包导入问题，使用文件路径更稳妥。
    """
    results = {}
    for f in TEST_FILES:
        print(f"\n=== Running {f} ===")
        try:
            mod_ns = runpy.run_path(f, run_name="__main__")
            # 如果文件中定义了 run()，优先调用
            if "run" in mod_ns and callable(mod_ns["run"]):
                res = mod_ns["run"]()
                results[f] = {"ok": True, "res": res}
                print("Result:", res)
            else:
                results[f] = {"ok": True, "res": None}
                print("No run() found, executed file.")
        except Exception as e:
            results[f] = {"ok": False, "error": str(e)}
            print("Error:", e)

    print("\n=== Summary ===")
    for k, v in results.items():
        print(k, "->", v)


if __name__ == "__main__":
    main()
