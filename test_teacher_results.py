import requests
import sys

# Test teacher results page
login_url = 'http://127.0.0.1:5000/login'
results_url = 'http://127.0.0.1:5000/teacher/results'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access teacher results page
    response = session.get(results_url)
    print(f"GET /teacher/results - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Teacher results page accessible!")
        if "All Test Results" in response.text:
            print("✅ Results page content loading correctly!")
        else:
            print("❌ Results page content issue")
    else:
        print("❌ Teacher results page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
