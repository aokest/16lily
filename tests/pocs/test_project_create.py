"""
复现用例 01：项目新建失败/成功路径对比

目的:
- 验证 `POST /projects/` 在缺少必填字段 `code` 时返回 400；补全字段后返回 201。

关联代码参考:
- 序列化器: [serializers.py:ProjectSerializer.Meta.read_only_fields](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/serializers.py#L415-L424)
- 视图集: [views.py:ProjectViewSet.perform_create](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L702-L721)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行项目新建用例：
    - 用例A：缺少 code，预期 400
    - 用例B：补全 code，预期 201
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token，请先执行: docker-compose exec web python manage.py ensure_admin"
    headers = make_auth_headers(token)

    # 用例A：缺少 code
    payload_a = {
        "name": "测试项目A",
        "description": "缺少编号，验证 400",
    }
    resp_a = requests.post(f"{BASE_URL}/projects/", headers=headers, data=json.dumps(payload_a), timeout=15)
    print("[Project-A] status=", resp_a.status_code, "body=", resp_a.text[:200])

    # 用例B：补全 code
    payload_b = {
        "name": "测试项目B",
        "code": "TEST-PROJ-001",
        "description": "补全编号，预期 201",
    }
    resp_b = requests.post(f"{BASE_URL}/projects/", headers=headers, data=json.dumps(payload_b), timeout=15)
    print("[Project-B] status=", resp_b.status_code, "body=", resp_b.text[:200])

    return {
        "A_status": resp_a.status_code,
        "B_status": resp_b.status_code,
    }


if __name__ == "__main__":
    print(run())

