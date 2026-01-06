
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def init_report_to():
    # 查找管理员或第一个经理作为默认汇报对象
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("未找到管理员用户")
        return

    # 为所有没有汇报对象的用户设置默认汇报对象
    profiles = UserProfile.objects.filter(report_to__isnull=True).exclude(user=admin)
    count = 0
    for profile in profiles:
        profile.report_to = admin
        profile.save()
        count += 1
    
    print(f"成功为 {count} 个用户初始化了汇报对象（默认：{admin.username}）")

if __name__ == "__main__":
    init_report_to()
