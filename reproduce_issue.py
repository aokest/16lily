import os
import django
import sys

# Add current directory to path so backend module can be found
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

try:
    user = User.objects.get(username='admin')
    print(f"User: {user}")
    
    try:
        profile = user.profile
        print(f"Profile found: {profile}")
        print(f"Job Series: {getattr(profile, 'job_series', 'None')}")
    except Exception as e:
        print(f"Error accessing profile: {e}")

except Exception as e:
    print(f"Error getting user: {e}")
