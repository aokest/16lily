"""
复现用例 02：项目卡片编辑保存无日志/修复后日志生成

目的:
- 验证 `PATCH /project-cards/{id}/` 修改 `sub_stage` 能触发 `ProjectChangeLog` 记录。

关联代码参考:
- 模型: [models.py:ProjectCard.save](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/models.py#L905-L921)
- 视图集: [views.py:ProjectCardViewSet.perform_update](file:///Users/aoke/code%20test/%E5%95%86%E6%9C%BA%E8%B7%9F%E8%BF%9B%E5%8F%8A%E4%B8%9A%E7%BB%9F%E8%AE%A1/opportunity_system/core/views.py#L740-L743)
"""

import json
import requests
from auth_utils import get_admin_token, make_auth_headers


BASE_URL = "http://localhost:8000/api"


def ensure_project_and_card(headers: dict) -> tuple[int, int]:
    """
    保证存在一个项目与其卡片，返回 (project_id, card_id)

    - 若不存在项目，则创建一个简单项目。
    - 创建一张卡片并返回其 ID。
    """
    # 创建项目
    proj = requests.post(f"{BASE_URL}/projects/", headers=headers, data=json.dumps({
        "name": "卡片日志验证项目",
        "code": "CARD-LOG-001"
    }), timeout=15).json()
    project_id = proj.get("id") or proj.get("pk")

    # 创建卡片
    card = requests.post(f"{BASE_URL}/project-cards/", headers=headers, data=json.dumps({
        "project": project_id,
        "title": "子阶段变更测试",
        "sub_stage": "设计中"
    }), timeout=15).json()
    card_id = card.get("id") or card.get("pk")

    return project_id, card_id


def run():
    """
    执行步骤:
    1) 创建项目+卡片
    2) PATCH 卡片 `sub_stage` 字段
    3) 查询项目 `change_logs` 验证新增记录
    """
    token = get_admin_token(BASE_URL)
    assert token, "无法获取管理员 Token"
    headers = make_auth_headers(token)

    project_id, card_id = ensure_project_and_card(headers)
    # 更新子阶段
    resp_patch = requests.patch(
        f"{BASE_URL}/project-cards/{card_id}/",
        headers=headers,
        data=json.dumps({"sub_stage": "测试中"}),
        timeout=15,
    )
    print("[Card-PATCH] status=", resp_patch.status_code)

    # 查询项目变更日志
    proj = requests.get(f"{BASE_URL}/projects/{project_id}/", headers=headers, timeout=15).json()
    logs = (proj or {}).get("change_logs") or []
    print("[Card-Logs] count=", len(logs))
    return {"patch_status": resp_patch.status_code, "log_count": len(logs)}


if __name__ == "__main__":
    print(run())

