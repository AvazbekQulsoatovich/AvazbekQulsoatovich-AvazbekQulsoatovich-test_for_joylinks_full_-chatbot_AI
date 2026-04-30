import requests
import sys

# Test admin results page
login_url = 'http://127.0.0.1:5000/login'
results_url = 'http://127.0.0.1:5000/admin/results'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access results page
    response = session.get(results_url)
    print(f"GET /admin/results - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin results page accessible!")
        if "All Test Results" in response.text:
            print("✅ Results page content loading correctly!")
        else:
            print("❌ Results page content issue")
    else:
        print("❌ Admin results page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
