import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Opportunity, OpportunityLog, TodoTask
from core.models_transfer import OpportunityTransferApplication

def run():
    print("--- Verifying Opportunity Transfer Logic (Signal Based) ---")
    
    # 1. Create/Get Users
    admin_user, _ = User.objects.get_or_create(username='admin_test')
    target_user, _ = User.objects.get_or_create(username='target_test')
    if not admin_user.is_superuser:
        admin_user.is_superuser = True
        admin_user.save()
    
    # 2. Create Opportunity
    opp, created = Opportunity.objects.get_or_create(
        name="Test Transfer Opp",
        defaults={
            'creator': admin_user,
            'sales_manager': admin_user,
            'amount': 10000
        }
    )
    print(f"Opportunity: {opp}")

    # 3. Create Transfer Log
    print("Creating OpportunityLog with action='商机移交'...")
    log = OpportunityLog.objects.create(
        opportunity=opp,
        operator=admin_user,
        action='商机移交',
        content='Testing Signal Logic',
        transfer_target=target_user
    )
    print(f"Log Created: ID={log.id}")

    # 4. Verify Side Effects
    # Check Application
    app = OpportunityTransferApplication.objects.filter(opportunity=opp, status='PENDING').last()
    if app:
        print(f"[SUCCESS] Transfer Application Created: ID={app.id}, Target={app.target_owner}")
    else:
        print("[FAILURE] Transfer Application NOT Found!")

    # Check TodoTask
    task = TodoTask.objects.filter(title__contains=opp.name).last()
    if task:
        print(f"[SUCCESS] TodoTask Created: ID={task.id}, Assignee={task.assignee}")
    else:
        print("[FAILURE] TodoTask NOT Found!")

if __name__ == '__main__':
    run()
