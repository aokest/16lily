import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/aoke/code test/商机跟进及业绩统计/16lily')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.services.ai_service import AIService
from django.contrib.auth.models import User

def test_ai_polish():
    service = AIService()
    print(f"Using AI Config: {service.config}")
    
    text = "今天写了代码，修复了Bug。"
    user = User.objects.first()
    
    print(f"Testing polish for text: {text}")
    try:
        result = service.polish_daily_report(text, user=user)
        print(f"Result: {result}")
        if result == text:
            print("Warning: Result is same as input. AI might have failed silently.")
    except Exception as e:
        print(f"Error during AI polish: {e}")

if __name__ == "__main__":
    test_ai_polish()
