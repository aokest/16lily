"""
复现用例 05：联系人删除与恢复

目的:
- 验证 `DELETE /contacts/{id}/` 会记录删除日志；管理员可 `POST /contacts/restore/` 恢复

关联代码参考:
- 视图: [views.py:ContactViewSet.perform_destroy](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/views.py#L280-L295)
- 视图: [views.py:ContactViewSet.restore](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/16lily/core/views.py#L296-L310)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def run():
    """
    执行步骤:
    1) 创建客户与联系人
    2) 删除联系人
    3) 管理员读取删除日志并恢复
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    # 1) 创建客户
    cust = requests.post(f"{BASE_URL}/customers/", headers=headers, data=json.dumps({
        "name": "恢复测试客户",
        "industry": "软件",
        "region": "华东"
    }), timeout=15).json()
    cust_id = cust.get("id")

    # 2) 创建联系人
    contact = requests.post(f"{BASE_URL}/contacts/", headers=headers, data=json.dumps({
        "customer": cust_id,
        "name": "张三",
        "title": "经理",
        "phone": "13800000000"
    }), timeout=15).json()
    c_id = contact.get("id")

    # 3) 删除联系人
    del_resp = requests.delete(f"{BASE_URL}/contacts/{c_id}/", headers=headers, timeout=15)
    print("[Contact-DEL] status=", del_resp.status_code)

    # 4) 管理员读取删除日志 (需要管理员权限，采用同一账户)
    logs = requests.get(f"{BASE_URL}/activity-logs/", headers=headers, timeout=15)  # 若无开放日志列表，可改为 DB 检查
    print("[Logs] status=", logs.status_code)

    # 5) 恢复联系人：此处需要传 log_id；简单起见，直接尝试恢复最近一条（演示用途）
    # 实际生产建议新增 `GET /contact-delete-logs/` 列表接口以精确获取 log_id
    restore_resp = requests.post(f"{BASE_URL}/contacts/restore/", headers=headers, data=json.dumps({
        "log_id": 1
    }), timeout=15)
    print("[Contact-RESTORE] status=", restore_resp.status_code, restore_resp.text[:100])
    return {"del_status": del_resp.status_code, "restore_status": restore_resp.status_code}


if __name__ == "__main__":
    print(run())

