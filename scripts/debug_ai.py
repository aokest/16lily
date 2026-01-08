import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/aoke/code test/商机跟进及业绩统计/16lily')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.services.ai_service import AIService
from core.models import AIConfiguration, PromptTemplate

def debug_ai():
    print("--- 1. Checking Configuration ---")
    active_config = AIConfiguration.objects.filter(is_active=True).first()
    if active_config:
        print(f"Active Config: {active_config.name}")
        print(f"Provider: {active_config.provider}")
        print(f"Model: {active_config.model_name}")
        print(f"Base URL: {active_config.base_url}")
        print(f"API Key: {active_config.api_key[:5]}..." if active_config.api_key else "No API Key")
    else:
        print("❌ No active AI Configuration found!")
        return

    print("\n--- 2. Checking Prompt Template ---")
    # Check if there's an active prompt template for OPPORTUNITY
    template = PromptTemplate.objects.filter(scene='OPPORTUNITY', is_active=True).order_by('-updated_at').first()
    if template:
        print(f"Active Template Found: {template.name}")
        print("Template Content Preview:")
        print(template.template[:200] + "...")
    else:
        print("Using Code-Default Prompt (No active template in DB)")

    print("\n--- 3. Testing Analysis ---")
    text = "新增一个商机，客户是腾讯科技，预计金额500万，下个月签约。"
    service = AIService()
    
    # We call the internal method to see raw output if possible, but _call_llm_json handles it.
    # Let's verify what parse_opportunity returns.
    print(f"Input Text: {text}")
    
    try:
        result = service.parse_opportunity(text)
        print("\n--- 4. Result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if not result:
            print("❌ Result is None")
        elif 'error' in result:
            print(f"❌ Error in result: {result['error']}")
            if 'raw' in result:
                print(f"Raw Output: {result['raw']}")
        else:
            print("✅ Parsed Successfully")
            
    except Exception as e:
        print(f"❌ Exception during call: {e}")

if __name__ == "__main__":
    debug_ai()
