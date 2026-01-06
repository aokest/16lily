import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    try:
        response = requests.post(f"{BASE_URL}/api-token-auth/", json={"username": "admin", "password": "admin123"})
        print(f"Token response: {response.status_code}")
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_endpoint(endpoint, token):
    headers = {"Authorization": f"Token {token}"}
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers)
        print(f"Testing {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"Error content: {response.text[:500]}...") # Increased content length for better debugging
        else:
            print(f"Success {endpoint}")
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")

if __name__ == "__main__":
    # Wait for a bit to ensure server reload (if any)
    print("Starting API tests...")
    token = get_token()
    if token:
        print(f"Got token: {token[:10]}...")
        test_endpoint("opportunities", token)
        test_endpoint("customers", token)
        test_endpoint("contacts", token)
        test_endpoint("reports/performance", token)
        test_endpoint("social-stats", token)
        test_endpoint("social-accounts", token)
        test_endpoint("projects", token)
        test_endpoint("daily-reports", token)
    else:
        print("Skipping tests due to token failure")
