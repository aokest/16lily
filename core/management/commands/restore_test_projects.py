from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Project, Customer, Opportunity
from django.utils import timezone
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Restore test projects if missing'

    def handle(self, *args, **options):
        # if Project.objects.count() > 0:
        #     self.stdout.write('Projects already exist. Skipping restoration.')
        #     return

        self.stdout.write('Restoring test projects...')
        
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            # Fallback to first user
            admin = User.objects.first()
            if not admin:
                self.stdout.write('No user found.')
                return

        # Find some customers and opportunities
        customers = list(Customer.objects.all())
        opportunities = list(Opportunity.objects.all())
        
        if not customers:
             customers = [Customer.objects.create(name=f'Test Customer {i}', owner=admin) for i in range(3)]
        
        projects_data = [
            {
                'name': '智慧城市大脑一期',
                'status': 'IN_PROGRESS',
                'budget': 5000000,
                'description': '城市级数据中台与指挥中心建设'
            },
            {
                'name': '企业数字化转型咨询',
                'status': 'PLANNING',
                'budget': 800000,
                'description': '集团整体数字化规划'
            },
            {
                'name': '智能制造产线改造',
                'status': 'COMPLETED',
                'budget': 12000000,
                'description': '车间IoT设备接入与MES系统升级'
            },
             {
                'name': '政务云迁移服务',
                'status': 'TERMINATED',
                'budget': 200000,
                'description': '因政策调整中止'
            }
        ]
        
        for i, data in enumerate(projects_data):
            # Check if exists
            if Project.objects.filter(name=data['name']).exists():
                continue

            cust = random.choice(customers)
            opp = random.choice(opportunities) if opportunities else None
            
            p = Project.objects.create(
                name=data['name'],
                code=f"PRJ-2025-{random.randint(1000,9999)}",
                customer=cust,
                opportunity=opp,
                status=data['status'],
                budget=data['budget'],
                description=data['description'],
                owner=admin,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=90)
            )
            self.stdout.write(f"Created project: {p.name}")
            
        self.stdout.write(self.style.SUCCESS('Done.'))
