from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Ensures an admin user exists'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            u = User.objects.get(username='admin')
            u.set_password('admin123')
            u.save()
            self.stdout.write(self.style.SUCCESS('Successfully reset admin password'))
