import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Opportunity, Customer, OpportunityLog

def run():
    print("🌱 Seeding dummy data for SQLite demo...")
    
    # 1. Create Users
    sales_user, _ = User.objects.get_or_create(username='sales_demo', defaults={'email': 'sales@demo.com'})
    sales_user.set_password('123456')
    sales_user.save()
    
    manager_user, _ = User.objects.get_or_create(username='manager_demo', defaults={'email': 'manager@demo.com'})
    manager_user.set_password('123456')
    manager_user.save()

    # 2. Create Customer
    customer, _ = Customer.objects.get_or_create(
        name="未来科技集团",
        defaults={'industry': "AI", 'scale': 'LARGE', 'status': 'ACTIVE', 'owner': sales_user}
    )

    # 3. Create Opportunity
    opp, created = Opportunity.objects.get_or_create(
        name="AI 大模型私有化部署项目",
        defaults={
            'customer': customer,
            'sales_manager': sales_user,
            'creator': sales_user,
            'amount': 5000000,
            'stage': 'PROPOSAL',
            'status': 'ACTIVE'
        }
    )
    
    if created:
        print(f"Created Opportunity: {opp.name}")
        
        # 4. Create Logs
        OpportunityLog.objects.create(
            opportunity=opp,
            operator=sales_user,
            action='创建商机',
            content="初步接触客户，需求明确",
            created_at=timezone.now() - timedelta(days=2)
        )
        OpportunityLog.objects.create(
            opportunity=opp,
            operator=sales_user,
            action='赢单',
            content="客户确认中标，准备合同",
            created_at=timezone.now()
        )
    else:
        print("Opportunity already exists")

    print("✅ Seed complete!")

if __name__ == '__main__':
    run()
