"""
复现用例 07：商机扩展字段兼容

目的:
- 验证 `POST /opportunities/` 在提交扩展字段（如 win_rate）时不报错

关联代码参考:
- 序列化器: [serializers.py:OpportunitySerializer](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/serializers.py#L297-L330)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 创建商机，携带扩展字段
    2) 预期成功返回 201
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    payload = {
        "name": "企业安全项目商机",
        "customer_company": "示例科技有限公司",
        "stage": "CONTACT",
        "amount": "500000",
        # 扩展字段（后端不持久化，应忽略而不报错）
        "expected_sign_date": "2026-03-01",
        "win_rate": 60,
        "customer_name": "李四",
        "customer_email": "lisi@example.com"
    }
    resp = requests.post(f"{BASE_URL}/opportunities/", headers=headers, data=json.dumps(payload), timeout=15)
    print("[Opportunity] status=", resp.status_code, "body=", resp.text[:200])
    return {"status": resp.status_code}


if __name__ == "__main__":
    print(run())

