from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Opportunity, OpportunityLog, PerformanceTarget, DepartmentModel as Department
from django.utils import timezone
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Initialize demo data for dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # 1. Ensure Admin
        admin, _ = User.objects.get_or_create(username='admin')
        
        # 2. Set Company Target for 2025
        target, created = PerformanceTarget.objects.get_or_create(
            year=2025,
            quarter=0, # Full Year
            department=Department.SALES,
            user=None,
            defaults={
                'target_amount': Decimal('50000000.00'), # 5000万
                'target_gross_profit': Decimal('20000000.00'),
                'target_revenue': Decimal('45000000.00')
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created 2025 Company Target: 5000万'))
        else:
            self.stdout.write('ℹ️ 2025 Target already exists')

        # 3. Create some random logs if few exist
        if OpportunityLog.objects.count() < 5:
            ops = Opportunity.objects.all()
            if ops.exists():
                actions = ['更新进度', '客户拜访', '方案汇报', '商务谈判', '赢得商机']
                for _ in range(10):
                    op = random.choice(ops)
                    action = random.choice(actions)
                    OpportunityLog.objects.create(
                        opportunity=op,
                        operator=admin,
                        action=action,
                        content=f"进行了{action}，情况良好。",
                        stage_snapshot=op.stage
                    )
                self.stdout.write(self.style.SUCCESS('✅ Created random logs'))
            else:
                self.stdout.write('⚠️ No opportunities found to create logs for.')
        
        self.stdout.write(self.style.SUCCESS('Done.'))