import requests
import sys

# Test admin students page
login_url = 'http://127.0.0.1:5000/login'
students_url = 'http://127.0.0.1:5000/admin/students'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access students page
    response = session.get(students_url)
    print(f"GET /admin/students - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin students page accessible!")
        if "All Students" in response.text:
            print("✅ Students page content loading correctly!")
        else:
            print("❌ Students page content issue")
    else:
        print("❌ Admin students page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
