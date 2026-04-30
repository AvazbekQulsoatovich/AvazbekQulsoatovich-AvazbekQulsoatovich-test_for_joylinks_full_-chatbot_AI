import requests
import sys

# Test student dashboard page
login_url = 'http://127.0.0.1:5000/login'
student_dashboard_url = 'http://127.0.0.1:5000/student/dashboard'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access student dashboard
    response = session.get(student_dashboard_url)
    print(f"GET /student/dashboard - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Student dashboard page accessible!")
        if "Student Dashboard" in response.text:
            print("✅ Student dashboard page content loading correctly!")
        else:
            print("❌ Student dashboard page content issue")
    else:
        print("❌ Student dashboard page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
