import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import AIConfiguration

print("--- AI Configuration Check ---")
configs = AIConfiguration.objects.all()
print(f"Total Configs: {configs.count()}")

for c in configs:
    user_str = c.user.username if c.user else "None (System-wide)"
    print(f"ID: {c.id}, Name: {c.name}, User: {user_str}, Active: {c.is_active}")
