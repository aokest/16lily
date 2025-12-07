import os
import django
import sys

# Assume we are in the project root (where manage.py is)
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Opportunity, AIConfiguration, TodoTask, Competition
from django.apps import apps
from django.db.models.signals import pre_save

def verify():
    print("Running verification...")
    
    # 1. Check if signals are registered
    receivers = pre_save.has_listeners(Opportunity)
    if receivers:
        print("✅ Signals registered for Opportunity.")
    else:
        print("❌ Signals NOT registered for Opportunity.")

    # 2. Check Models for AI fields
    try:
        Opportunity._meta.get_field('ai_raw_text')
        print("✅ Opportunity has ai_raw_text.")
    except:
        print("❌ Opportunity MISSING ai_raw_text.")

    try:
        Competition._meta.get_field('ai_raw_text')
        print("✅ Competition has ai_raw_text.")
    except:
        print("❌ Competition MISSING ai_raw_text.")
        
    # 3. Check AI Config model
    if AIConfiguration.objects.count() == 0:
        print("⚠️ No AI Configuration found. Please add one in Admin.")
    else:
        print(f"✅ Found {AIConfiguration.objects.count()} AI Configuration(s).")

    print("\nVerification complete.")

if __name__ == "__main__":
    verify()
