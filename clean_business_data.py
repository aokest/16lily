import os
import django

# 设置环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    PerformanceTarget, Opportunity, OpportunityTeamMember, OpportunityLog,
    Project, ProjectCard, ProjectLog, Customer, Contact, CustomerTag,
    Notification, DailyReport, SocialAccount, SocialStats
)

def clean_data():
    print("🚀 开始清理云端业务脏数据...")
    
    # 1. 清理业绩目标 (红框1, 2的核心)
    count = PerformanceTarget.objects.all().count()
    PerformanceTarget.objects.all().delete()
    print(f"✅ 已清理 PerformanceTarget: {count} 条")
    
    # 2. 清理商机及其关联数据 (影响已完成金额和预测)
    count = Opportunity.objects.all().count()
    Opportunity.objects.all().delete() # 级联删除 TeamMember 和 Log
    print(f"✅ 已清理 Opportunity: {count} 条")
    
    # 3. 清理项目及其关联数据
    count = Project.objects.all().count()
    Project.objects.all().delete() # 级联删除 Card 和 Log
    print(f"✅ 已清理 Project: {count} 条")
    
    # 4. 清理通知和待办事项 (红框3)
    count = Notification.objects.all().count()
    Notification.objects.all().delete()
    print(f"✅ 已清理 Notification/Todo: {count} 条")
    
    # 5. 清理客户与联系人
    count_c = Customer.objects.all().count()
    Customer.objects.all().delete()
    print(f"✅ 已清理 Customer: {count_c} 条")
    
    # 6. 清理日报
    count = DailyReport.objects.all().count()
    DailyReport.objects.all().delete()
    print(f"✅ 已清理 DailyReport: {count} 条")

    # 7. 清理社交媒体统计 (如果有)
    SocialAccount.objects.all().delete()
    SocialStats.objects.all().delete()
    print(f"✅ 已清理 SocialMedia 数据")

    print("\n✨ 业务数据清理完成！")
    print("🔒 组织架构（用户、部门、岗位）已受保护，未做任何修改。")

if __name__ == "__main__":
    clean_data()
