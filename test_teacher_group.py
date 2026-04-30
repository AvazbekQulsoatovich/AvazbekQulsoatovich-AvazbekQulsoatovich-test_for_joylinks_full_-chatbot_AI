import requests
import sys

# Test teacher add group page
login_url = 'http://127.0.0.1:5000/login'
add_group_url = 'http://127.0.0.1:5000/teacher/groups/add'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access add group page
    response = session.get(add_group_url)
    print(f"GET /teacher/groups/add - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Teacher add group page accessible!")
        if "Add New Group" in response.text:
            print("✅ Add group page content loading correctly!")
        else:
            print("❌ Add group page content issue")
    else:
        print("❌ Teacher add group page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
