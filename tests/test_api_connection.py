
import requests
import sys
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
USERNAME = "admin"
PASSWORD = "admin123"

def get_token():
    url = f"{BASE_URL}/api-token-auth/"
    try:
        response = requests.post(url, data={"username": USERNAME, "password": PASSWORD}, timeout=5)
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"✅ Token obtained: {token[:10]}...")
            return token
        else:
            print(f"❌ Failed to get token: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_ai_configs(token):
    url = f"{BASE_URL}/ai/configs/"
    headers = {"Authorization": f"Token {token}"}
    try:
        print(f"Testing {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response Status: {response.status_code}")
            print(f"✅ API Response Data: {data}")
            results = data.get('results', [])
            if results:
                print(f"✅ Found {len(results)} configs.")
            else:
                print("⚠️ No configs found in 'results'.")
        else:
            print(f"❌ API Request Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("--- Starting API Connection Test ---")
    token = get_token()
    if token:
        test_ai_configs(token)
