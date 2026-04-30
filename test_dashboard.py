import requests
import sys

# Test admin dashboard access
login_url = 'http://127.0.0.1:5000/login'
dashboard_url = 'http://127.0.0.1:5000/admin/dashboard'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access dashboard
    response = session.get(dashboard_url)
    print(f"GET /admin/dashboard - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin dashboard accessible!")
        if "Current Date:" in response.text:
            print("✅ Current time display working!")
        else:
            print("❌ Current time display issue")
    else:
        print("❌ Admin dashboard not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
