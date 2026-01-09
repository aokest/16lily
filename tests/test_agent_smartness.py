import os
import sys
import django
import json

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.services.ai_service import AIService
from django.contrib.auth import get_user_model

def test_smartness():
    print("--- Testing AI Service Smartness ---")
    
    # User's specific complaint input
    user_input = "创建一个客户，东北大学，教育行业，地点在沈阳，地点，行业等都打上标签。"
    
    service = AIService()
    
    # 1. Test Task Parsing (Intent Recognition)
    print(f"\nInput: {user_input}")
    print("Parsing task intent...")
    parsed_task = service.parse_task(user_input)
    print(f"Parsed Task Result: {json.dumps(parsed_task, indent=2, ensure_ascii=False)}")
    
    if parsed_task.get('intent') != 'create_customer':
        print("❌ FAIL: Intent not recognized as 'create_customer'")
    else:
        print("✅ PASS: Intent recognized")

    # 2. Test Entity Extraction (Regex/LLM)
    print("\nExtracting customer details...")
    # Mocking user if needed, but parse_customer relies mostly on text
    customer_data = service.parse_customer(user_input)
    print(f"Extracted Data: {json.dumps(customer_data, indent=2, ensure_ascii=False)}")
    
    # Validation Criteria based on user input
    expected_name = "东北大学"
    expected_industry = "教育"
    expected_region = "沈阳"
    
    failures = []
    if customer_data.get('name') != expected_name:
        failures.append(f"Name mismatch: Expected '{expected_name}', got '{customer_data.get('name')}'")
    
    # Fuzzy match for industry/region as they might be normalized
    if expected_industry not in (customer_data.get('industry') or ''):
         failures.append(f"Industry mismatch: Expected '{expected_industry}', got '{customer_data.get('industry')}'")
         
    if expected_region not in (customer_data.get('region') or ''):
         failures.append(f"Region mismatch: Expected '{expected_region}', got '{customer_data.get('region')}'")

    if failures:
        print("❌ FAIL: Extraction incomplete")
        for f in failures:
            print(f"  - {f}")
    else:
        print("✅ PASS: All fields extracted correctly")

if __name__ == "__main__":
    test_smartness()
