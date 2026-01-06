from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    """
    初始化系统角色和权限组
    """
    help = 'Initialize User Groups and Permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化角色权限...'))

        # 定义权限组及其对应的权限
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
                self.stdout.write(f"创建权限组: {group_name}")
            
            # 清除旧权限重新分配，确保准确
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
                            self.stdout.write(self.style.WARNING(f"  ! 找不到权限条目: {codename}"))
                except ContentType.DoesNotExist:
                     self.stdout.write(self.style.ERROR(f"  ! 找不到模型: {app_label}.{model_name}"))
        
        self.stdout.write(self.style.SUCCESS('✅ 角色权限组初始化完成！'))
