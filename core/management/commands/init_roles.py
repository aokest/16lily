from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from core.models import UserProfile, JobRole

class Command(BaseCommand):
    help = 'Initialize User Groups and Permissions based on Business Logic'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Role Initialization...'))

        # 1. Define Groups and Permissions
        roles_config = {
            'Group_Sales': {
                'models': [
                    ('core', 'opportunity', ['view', 'add', 'change']), 
                    ('core', 'opportunitylog', ['view', 'add']),
                ]
            },
            'Group_Tech': { 
                'models': [
                    ('core', 'opportunity', ['view']), 
                    ('core', 'opportunitylog', ['view', 'add']), 
                ]
            },
            'Group_Lab': {
                'models': [
                    ('core', 'opportunity', ['view']),
                    ('core', 'opportunitylog', ['view']),
                ]
            },
            'Group_Manager': { 
                'models': [
                    ('core', 'opportunity', ['view', 'add', 'change', 'delete']),
                    ('core', 'opportunitylog', ['view', 'add', 'change']),
                ]
            }
        }

        for group_name, config in roles_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"Created group: {group_name}")
            
            # Clear existing permissions to ensure strict sync
            group.permissions.clear()

            for app_label, model_name, actions in config['models']:
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                    for action in actions:
                        codename = f'{action}_{model_name}'
                        try:
                            perm = Permission.objects.get(content_type=content_type, codename=codename)
                            group.permissions.add(perm)
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"  ! Permission not found: {codename}"))
                except ContentType.DoesNotExist:
                     self.stdout.write(self.style.ERROR(f"  ! Model not found: {app_label}.{model_name}"))
        
        self.stdout.write(self.style.SUCCESS('✅ Roles and Permissions Definitions Updated.'))

        # 2. Sync Existing Users (Fix for users created before rules were set)
        self.stdout.write(self.style.SUCCESS('🔄 Syncing existing users...'))
        for profile in UserProfile.objects.all():
            user = profile.user
            role = profile.job_role
            target_group_name = None

            if role in [JobRole.SALES_REP]:
                target_group_name = 'Group_Sales'
            elif role in [JobRole.PRODUCT, JobRole.TEST, JobRole.IMPL, JobRole.FRONTEND, JobRole.BACKEND, JobRole.UI, JobRole.PRE_SALES, JobRole.POC]:
                target_group_name = 'Group_Tech'
            elif role in [JobRole.LAB_XIAORANG, JobRole.LAB_GAMMA]:
                target_group_name = 'Group_Lab'
            elif role in [JobRole.MANAGER]:
                target_group_name = 'Group_Manager'
            
            if target_group_name:
                try:
                    group = Group.objects.get(name=target_group_name)
                    # Only add if not already in group to avoid duplicate db calls (though add is safe)
                    if not user.groups.filter(name=target_group_name).exists():
                        user.groups.clear() # Enforce single group policy
                        user.groups.add(group)
                        self.stdout.write(f"  -> Assigned {user.username} ({role}) to {target_group_name}")
                    
                    if not user.is_staff:
                        user.is_staff = True
                        user.save()
                        self.stdout.write(f"  -> Enabled staff access for {user.username}")
                except Group.DoesNotExist:
                    pass
        
        self.stdout.write(self.style.SUCCESS('✅ User Sync Completed!'))
