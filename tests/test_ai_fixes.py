
import os
import django
import sys
import re

# Setup Django environment
sys.path.append('/Users/aoke/code test/商机跟进及业绩统计/16lily')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import AIConfiguration
from core.services.ai_service import AIService

def test_ai_config_visibility():
    print("\n--- Testing AI Config Visibility ---")
    configs = AIConfiguration.objects.filter(user__isnull=True)
    if configs.exists():
        print(f"✅ Success: Found {configs.count()} global AI configs.")
        for c in configs:
            print(f"   - {c.name} (Active: {c.is_active})")
    else:
        print("❌ Failure: No global AI configs found.")

def test_call_llm_history():
    print("\n--- Testing _call_llm History Param ---")
    service = AIService()
    # Mock _call_llm to avoid actual API call, just check signature
    try:
        # We are checking if it *accepts* the argument, not the result
        # But we can't easily check signature of bound method without inspection
        # So we'll try to call it with a dummy config if possible, or inspect
        import inspect
        sig = inspect.signature(service._call_llm)
        if 'history' in sig.parameters:
            print("✅ Success: _call_llm accepts 'history' parameter.")
        else:
            print("❌ Failure: _call_llm does NOT accept 'history' parameter.")
    except Exception as e:
        print(f"❌ Error inspecting _call_llm: {e}")

def test_customer_regex():
    print("\n--- Testing Customer Regex ---")
    text = "创建一个客户，东北大学，教育行业，地点在沈阳"
    # Regex from ai_service.py
    m_name = re.search(r'客户名称[:：]\s*([^\s，,]+)', text) or \
             re.search(r'(?:新建|创建)(?:一个|一项)?客户[，, ]\s*([^\s，,]{2,40})', text) or \
             re.search(r'客户[，, ]\s*([^\s，,]{2,40})', text)
    
    if m_name:
        print(f"✅ Success: Matched customer name: '{m_name.group(1)}'")
    else:
        print("❌ Failure: Failed to match customer name.")

if __name__ == "__main__":
    test_ai_config_visibility()
    test_call_llm_history()
    test_customer_regex()
