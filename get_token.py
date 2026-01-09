import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
username = 'admin'
try:
    user = User.objects.get(username=username)
except User.DoesNotExist:
    # Try to find any superuser
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        # Create one if not exists (careful with password)
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Created new admin user")

token, created = Token.objects.get_or_create(user=user)
print(f"TOKEN: {token.key}")
