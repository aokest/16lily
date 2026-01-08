"""
复现用例 08：业绩目标批量更新

目的:
- 验证 `POST /performance-targets/bulk_update_targets/` 能 upsert 月度目标

关联代码参考:
- 视图: [views.py:PerformanceTargetViewSet.bulk_update_targets](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/views.py#L202-L262)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 提交年份+部门+targets 列表
    2) 预期返回 updated 计数
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    payload = {
        "year": 2026,
        "department": "SALES",
        "targets": [
            {"month": 1, "target_amount": 100000},
            {"month": 2, "target_amount": 120000},
            {"month": 3, "target_amount": 150000},
        ]
    }
    resp = requests.post(
        f"{BASE_URL}/performance-targets/bulk_update_targets/",
        headers=headers,
        data=json.dumps(payload),
        timeout=20,
    )
    print("[Targets-Bulk] status=", resp.status_code, "body=", resp.text[:200])
    ok = resp.status_code == 200 and "updated" in resp.text
    return {"status": resp.status_code, "ok": ok}


if __name__ == "__main__":
    print(run())

