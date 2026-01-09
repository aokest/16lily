import os
import sys
import django
from django.conf import settings

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

def test_endpoints():
    print("--- Starting Reproduction Test ---")
    
    # Create or get test user
    username = 'test_repro_user'
    password = 'password123'
    email = 'test_repro@example.com'
    
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()
        print(f"Created user: {username}")
    else:
        print(f"Using existing user: {username}")
        
    client = APIClient()
    client.force_authenticate(user=user)
    
    # 1. Test 'ai/configs/' (Used by ChatWindow.vue)
    print("\n[Test 1] GET /api/ai/configs/")
    try:
        response = client.get('/api/ai/configs/')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Response Data Keys: {data.keys()}")
            print(f"Config Count: {len(results)}")
            if len(results) > 0:
                print(f"First Config: ID={results[0]['id']}, Name={results[0]['name']}")
            else:
                print("WARNING: No configs returned!")
        else:
            print(f"Error: {response.content}")
    except Exception as e:
        print(f"Exception: {e}")

    # 2. Test 'admin/ai-configs/' (Used by AIConfig.vue)
    print("\n[Test 2] GET /api/admin/ai-configs/")
    try:
        response = client.get('/api/admin/ai-configs/')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success: Endpoint exists.")
        else:
            print(f"Failure: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

    # 3. Test 'ai/test-connection/' (Used by ChatWindow.vue)
    print("\n[Test 3] POST /api/ai/test-connection/ (With Config ID)")
    # Get a valid config ID first
    from core.models import AIConfiguration
    config = AIConfiguration.objects.first()
    if config:
        print(f"Testing with Config ID: {config.id}")
        payload = {'config_id': config.id}
        response = client.post('/api/ai/test-connection/', payload, format='json')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print("Skipping Test 3 (No configs in DB)")

    # 4. Test 'ai/test-connection/' (Without Config ID - Reproducing "Config ID required")
    print("\n[Test 4] POST /api/ai/test-connection/ (Missing Config ID)")
    payload = {}
    response = client.post('/api/ai/test-connection/', payload, format='json')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check if response message is Chinese
    msg = response.json().get('error', '')
    if '请提供配置ID' in msg:
        print("✅ Error message is in Chinese.")
    else:
        print(f"❌ Error message is NOT Chinese: '{msg}'")

if __name__ == "__main__":
    test_endpoints()
