from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from core.models import (
    DepartmentModel, UserProfile,
    Customer, Opportunity, MarketActivity, Competition,
    ApprovalRequest, ApprovalStatus
)


class Command(BaseCommand):
    help = "Verify approval flows by creating sample data and printing results"

    def create_user(self, username, password, is_superuser=False, job_role='MEMBER', dept: DepartmentModel = None, reports_to: UserProfile = None):
        user, created = User.objects.get_or_create(username=username, defaults={
            'is_superuser': is_superuser,
            'is_staff': True if is_superuser else False,
        })
        if password:
            user.set_password(password)
            user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={
            'job_role': job_role,
            'department': DepartmentModel.Category.FUNCTION
        })
        if dept:
            profile.department_link = dept
        profile.job_role = job_role
        profile.reports_to = reports_to
        profile.save()
        return user, profile

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Initializing departments...'))
        d_sales, _ = DepartmentModel.objects.get_or_create(name='销售部', defaults={'category': DepartmentModel.Category.SALES})
        d_game, _ = DepartmentModel.objects.get_or_create(name='春秋GAME', defaults={'category': DepartmentModel.Category.POC})
        d_marketing, _ = DepartmentModel.objects.get_or_create(name='集团市场部', defaults={'category': DepartmentModel.Category.FUNCTION})
        d_lily, _ = DepartmentModel.objects.get_or_create(name='十六军团', defaults={'category': DepartmentModel.Category.FUNCTION})

        self.stdout.write(self.style.NOTICE('Initializing users...'))
        admin, admin_profile = self.create_user('admin_approval', '123456', is_superuser=True, job_role='DIRECTOR', dept=d_lily)
 
        manager_sales, p_mgr_sales = self.create_user('manager_sales', '123456', job_role='MANAGER', dept=d_sales)
        manager_marketing, p_mgr_mkt = self.create_user('manager_marketing', '123456', job_role='MANAGER', dept=d_marketing)
        manager_game, p_mgr_game = self.create_user('manager_game', '123456', job_role='MANAGER', dept=d_game)

        # Set department managers
        d_sales.manager = manager_sales
        d_marketing.manager = manager_marketing
        d_game.manager = manager_game
        d_sales.save(); d_marketing.save(); d_game.save()

        employee_sales, p_emp_sales = self.create_user('employee_sales', '123456', job_role='SALES_REP', dept=d_sales, reports_to=p_mgr_sales)

        self.stdout.write(self.style.NOTICE('Creating test records...'))
        # Customer -> should create approval to sales manager
        cust, _ = Customer.objects.get_or_create(name='测试客户-审批', defaults={
            'owner': employee_sales,
            'status': 'POTENTIAL',
            'industry': '教育'
        })

        # Opportunity -> set approval_status=PENDING
        opp = Opportunity.objects.create(
            name='测试商机-审批',
            customer=cust,
            customer_company=cust.name,
            amount=123000,
            creator=employee_sales,
            sales_manager=manager_sales,
            approval_status=ApprovalStatus.PENDING
        )

        # Market Activity -> PENDING
        mkt = MarketActivity.objects.create(
            name='测试市场活动-审批',
            time='2025-12-10',
            location='北京',
            type='展会',
            status=ApprovalStatus.PENDING,
            creator=manager_marketing
        )

        # Competition -> PENDING
        comp = Competition.objects.create(
            name='测试赛事-审批',
            status=ApprovalStatus.PENDING,
            creator=manager_game
        )

        # Summaries
        ct_customer = ContentType.objects.get_for_model(Customer)
        ct_opportunity = ContentType.objects.get_for_model(Opportunity)
        ct_activity = ContentType.objects.get_for_model(MarketActivity)
        ct_competition = ContentType.objects.get_for_model(Competition)

        qs = ApprovalRequest.objects.all().order_by('-created_at')
        by_model = {
            'customer': qs.filter(content_type=ct_customer).count(),
            'opportunity': qs.filter(content_type=ct_opportunity).count(),
            'marketactivity': qs.filter(content_type=ct_activity).count(),
            'competition': qs.filter(content_type=ct_competition).count(),
        }
        self.stdout.write(self.style.SUCCESS(f"Approvals created -> {by_model}"))

        def who(req):
            return f"{req.content_type.model}#{req.object_id} -> approver={req.approver.username if req.approver else 'None'} status={req.status}"

        for req in qs[:10]:
            self.stdout.write(f" - {who(req)}")

        self.stdout.write(self.style.SUCCESS('OK: Data prepared. Use api-token-auth to obtain tokens for users: admin_approval / manager_sales / manager_marketing / manager_game (password: 123456).'))
