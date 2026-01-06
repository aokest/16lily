from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import DepartmentModel, UserProfile, JobRole, SocialMediaStats, ApprovalRequest, ApprovalStatus, Department

class Command(BaseCommand):
    help = 'Create a SocialMediaStats record and print approval routing'

    def handle(self, *args, **kwargs):
        dept, _ = DepartmentModel.objects.get_or_create(name='集团市场部', defaults={'category': DepartmentModel.Category.FUNCTION})
        mgr = User.objects.filter(username='manager_marketing').first()
        if not mgr:
            mgr = User.objects.create_user('manager_marketing', password='123456')
            prof = UserProfile.objects.create(user=mgr, job_role=JobRole.MANAGER, department=Department.GROUP_MARKETING, department_link=dept)
        dept.manager = mgr
        dept.save()
        stat = SocialMediaStats.objects.create(platform='测试账号-抖音', fans_count=8888, status=ApprovalStatus.PENDING, creator=mgr)
        count = ApprovalRequest.objects.filter(content_type__model='socialmediastats', object_id=stat.id).count()
        self.stdout.write(self.style.SUCCESS(f'Created SocialMediaStats#{stat.id}, approvals={count}'))
