"""
复现用例 03：AI 润色接口兼容字符串/字典返回

目的:
- 验证 `POST /daily-reports/{id}/polish/` 能正确写入 `polished_content`

关联代码参考:
- 视图集: [views.py:DailyReportViewSet.polish](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L754-L786)
"""

import json
import requests
from datetime import date
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 创建一条日报
    2) 调用 polish 动作
    3) 验证返回包含 polished_content
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    # 创建日报
    payload = {
        "date": date.today().isoformat(),
        "raw_content": "今天完成需求评审与任务拆分，准备进入开发阶段。",
        "status": "DRAFT"
    }
    report = requests.post(f"{BASE_URL}/daily-reports/", headers=headers, data=json.dumps(payload), timeout=15).json()
    rep_id = report.get("id")

    # 调用润色
    resp = requests.post(f"{BASE_URL}/daily-reports/{rep_id}/polish/", headers=headers, timeout=30)
    print("[Polish] status=", resp.status_code, "body=", resp.text[:200])
    ok = resp.status_code == 200 and "polished_content" in resp.text
    return {"polish_ok": ok, "status": resp.status_code}


if __name__ == "__main__":
    print(run())

