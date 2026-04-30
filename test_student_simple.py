import requests
import sys

# Simple test to see actual error
dashboard_url = 'http://127.0.0.1:5000/student/dashboard'

try:
    response = requests.get(dashboard_url)
    print(f"Direct access to student dashboard: {response.status_code}")
    print("Response content:")
    print(response.text)
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
