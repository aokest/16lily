import os
import django

# 设置环境
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
except ModuleNotFoundError:
    # 兼容容器内部路径 (容器内项目根目录可能没有外层文件夹名)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    django.setup()

from django.contrib.auth.models import User
from core.models import (
    Opportunity, 
    Notification, 
    Customer, 
    Contact, 
    OpportunityLog,
    OpportunityTeamMember,
    DailyReport
)

def clean_data():
    print("🚀 开始清理云端业务脏数据...")
    
    # 按照依赖关系顺序清理核心业务数据
    models_to_clean = [
        (OpportunityLog, "商机跟进日志"),
        (OpportunityTeamMember, "商机团队成员"),
        (Opportunity, "商机"),
        (Notification, "系统通知"),
        (DailyReport, "工作日报"),
        (Contact, "联系人"),
        (Customer, "客户"),
    ]

    for model, name in models_to_clean:
        try:
            count = model.objects.all().count()
            model.objects.all().delete()
            print(f"✅ 已清理 {name}: {count} 条")
        except Exception as e:
            print(f"❌ 清理 {name} 失败: {str(e)}")

    print("\n✨ 业务数据清理完成！")
    print("🔒 组织架构（用户、部门、岗位）已受保护，未做任何修改。")

if __name__ == "__main__":
    clean_data()
