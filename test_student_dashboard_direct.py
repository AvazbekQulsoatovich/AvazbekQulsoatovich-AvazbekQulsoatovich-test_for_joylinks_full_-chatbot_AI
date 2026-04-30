import requests
import sys

# Test student dashboard with proper session following
login_url = 'http://127.0.0.1:5000/login'
dashboard_url = 'http://127.0.0.1:5000/student/dashboard'

try:
    session = requests.Session()
    
    # Login as student
    login_data = {
        'username': 'student1',
        'password': 'student123'
    }
    response = session.post(login_url, data=login_data)
    print(f"Student login: {response.status_code}")
    
    # Follow redirects to get to dashboard
    response = session.get(dashboard_url)
    print(f"Student dashboard: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Student dashboard accessible!")
        if "Student Dashboard" in response.text:
            print("✅ Student dashboard content loading correctly!")
        else:
            print("❌ Student dashboard content issue")
    else:
        print("❌ Student dashboard not accessible")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
