"""
复现用例 04：业绩报表结构兼容校验

目的:
- 验证 `GET /reports/performance/` 返回结构包含 `totals/groups/monthly` 等键

关联代码参考:
- 视图: [views.py:PerformanceReportView.get](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/views.py#L425-L488)
"""

import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 查询部门年度报表
    2) 校验关键字段存在
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    params = {
        "group_by": "department",
        "scope": "department",
        "time_range": "year",
        "year": "2026",
    }
    resp = requests.get(f"{BASE_URL}/reports/performance/", headers=headers, params=params, timeout=15)
    print("[Perf] status=", resp.status_code)
    data = {}
    try:
        data = resp.json()
    except Exception:
        pass

    keys_ok = all(k in (data or {}) for k in ["totals", "groups"])
    return {"status": resp.status_code, "keys_ok": keys_ok}


if __name__ == "__main__":
    print(run())

