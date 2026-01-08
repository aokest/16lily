"""
复现用例 06：社媒账号保存字段兼容

目的:
- 验证 `POST /social-accounts/` 支持前端别名 `account_username` 并成功创建

关联代码参考:
- 序列化器: [serializers.py:SocialMediaAccountSerializer](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/serializers.py#L279-L296)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 使用前端字段别名创建社媒账号
    2) 预期返回 201
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    payload = {
        "platform": "WECHAT_OFFICIAL",
        "account_username": "公司公众号",
        "url": "https://weixin.qq.com/example"
    }
    resp = requests.post(f"{BASE_URL}/social-accounts/", headers=headers, data=json.dumps(payload), timeout=15)
    print("[SocialAccount] status=", resp.status_code, "body=", resp.text[:200])
    return {"status": resp.status_code}


if __name__ == "__main__":
    print(run())

