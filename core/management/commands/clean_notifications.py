from django.core.management.base import BaseCommand
from core.models import Notification
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = '清理通知系统中的脏数据（指向已删除对象的通知）'

    def handle(self, *args, **options):
        self.stdout.write('开始清理通知脏数据...')
        notifications = Notification.objects.all()
        count = 0
        for notice in notifications:
            if notice.content_type and notice.object_id:
                model_class = notice.content_type.model_class()
                if model_class:
                    obj_exists = model_class.objects.filter(pk=notice.object_id).exists()
                    is_soft_deleted = False
                    if obj_exists:
                        obj = model_class.objects.get(pk=notice.object_id)
                        is_soft_deleted = getattr(obj, 'is_deleted', False)
                    
                    if not obj_exists or is_soft_deleted:
                        reason = "已不存在" if not obj_exists else "已被标记删除"
                        self.stdout.write(f'删除无效通知: ID {notice.id}, 关联对象 {model_class.__name__}:{notice.object_id} {reason}')
                        notice.delete()
                        count += 1
                else:
                    self.stdout.write(f'删除无效通知: ID {notice.id}, 关联模型已不存在')
                    notice.delete()
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'清理完成，共删除 {count} 条脏数据。'))
