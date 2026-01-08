import os
import sys
import django
from django.utils import timezone

# Setup Django
sys.path.append('/Users/aoke/code test/商机跟进及业绩统计/16lily')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Opportunity, OpportunityLog

def backfill_logs():
    print("--- Starting Log Backfill ---")
    opportunities = Opportunity.objects.all()
    count = 0
    
    for opp in opportunities:
        # Check if it has any logs
        if opp.logs.count() == 0:
            print(f"Backfilling for: {opp.name}")
            
            # Create a "Created" log
            OpportunityLog.objects.create(
                opportunity=opp,
                operator=opp.creator if opp.creator else opp.sales_manager, # Fallback
                action="系统导入",
                content=f"历史商机数据回填：{opp.name}，金额：{opp.amount}",
                stage_snapshot=opp.get_stage_display(),
                created_at=opp.created_at # Keep original time order
            )
            count += 1
            
    print(f"--- Finished. Created {count} missing logs. ---")

if __name__ == "__main__":
    backfill_logs()
