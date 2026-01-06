from django.contrib.auth.models import Group, User
from typing import Optional
from .models import DepartmentModel

def resolve_effective_user(user: User) -> User:
    """
    解析有效操作者（支持助理同权代理）
    规则：若用户为“助理”且加入 ASSISTANT_PROXY 组，且存在汇报对象，则将有效用户解析为其汇报对象；否则为本人。
    """
    try:
        profile = getattr(user, "profile", None)
        if not profile:
            return user
        is_assistant = profile.job_category == 'ASSISTANT' or profile.job_rank == 'ASSISTANT'
        proxy_enabled = user.groups.filter(name="ASSISTANT_PROXY").exists()
        if is_assistant and proxy_enabled and profile.report_to:
            return profile.report_to
        return user
    except Exception:
        return user

def is_admin(user: User) -> bool:
    """
    判断是否为系统管理员（全域权限）
    """
    return bool(user and user.is_staff)

def is_dept_manager(user: User, department: Optional[DepartmentModel]) -> bool:
    """
    判断是否为指定部门负责人
    """
    if not user or not department:
        return False
    try:
        return department.manager_id == user.id
    except Exception:
        return False

def can_manage_department(user: User, department: Optional[DepartmentModel]) -> bool:
    """
    判断当前用户是否拥有管理指定部门的权限
    规则：
    - 管理员：True
    - 部门负责人：True
    - 助理同权：当用户为助理且开启 ASSISTANT_PROXY，代理为其汇报对象；若代理对象为部门负责人，则 True
    """
    if is_admin(user):
        return True
    if is_dept_manager(user, department):
        return True
    # 助理代理判断
    eff = resolve_effective_user(user)
    return is_dept_manager(eff, department)

