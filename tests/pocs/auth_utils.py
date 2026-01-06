"""
认证工具模块

提供获取管理员 Token 的辅助函数，供接口复现脚本调用。
依赖后端已创建管理员账户：admin/admin123（可通过 `manage.py ensure_admin` 保证）。
"""

import requests
from typing import Optional


def get_admin_token(base_url: str, username: str = "admin", password: str = "admin123") -> Optional[str]:
    """
    获取管理员账户的 DRF Token

    参数:
    - base_url: 后端 API 基础地址（不含末尾斜杠），例如 "http://localhost:8000/api"
    - username: 管理员用户名，默认 "admin"
    - password: 管理员密码，默认 "admin123"

    返回:
    - 成功时返回 token 字符串；失败时返回 None

    注意:
    - 需要后端启用了 `rest_framework.authtoken` 并在路由暴露 `api-token-auth/`
    """
    url = f"{base_url}/api-token-auth/"
    try:
        resp = requests.post(url, data={"username": username, "password": password}, timeout=10)
        if resp.status_code == 200 and isinstance(resp.json(), dict) and resp.json().get("token"):
            return resp.json()["token"]
        else:
            print(f"[Auth] 获取Token失败: status={resp.status_code}, body={resp.text}")
            return None
    except Exception as e:
        print(f"[Auth] 请求异常: {e}")
        return None


def make_auth_headers(token: str) -> dict:
    """
    构造携带 Token 的请求头

    参数:
    - token: 认证令牌字符串

    返回:
    - 包含 Authorization 与常用 Content-Type 的字典
    """
    return {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

