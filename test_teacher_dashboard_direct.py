import requests
import sys

# Test teacher dashboard with proper session following
login_url = 'http://127.0.0.1:5000/login'
dashboard_url = 'http://127.0.0.1:5000/teacher/dashboard'

try:
    session = requests.Session()
    
    # Login as teacher
    login_data = {
        'username': 'teacher1',
        'password': 'teacher123'
    }
    response = session.post(login_url, data=login_data)
    print(f"Teacher login: {response.status_code}")
    
    # Follow redirects to get to dashboard
    response = session.get(dashboard_url)
    print(f"Teacher dashboard: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Teacher dashboard accessible!")
        if "Teacher Dashboard" in response.text:
            print("✅ Teacher dashboard content loading correctly!")
        else:
            print("❌ Teacher dashboard content issue")
    else:
        print("❌ Teacher dashboard not accessible")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
