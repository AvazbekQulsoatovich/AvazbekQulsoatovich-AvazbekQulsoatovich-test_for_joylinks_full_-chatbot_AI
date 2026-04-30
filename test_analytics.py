import requests
import sys

# Test admin analytics page
login_url = 'http://127.0.0.1:5000/login'
analytics_url = 'http://127.0.0.1:5000/admin/analytics'

try:
    # First login to get session
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data)
    
    # Now access analytics page
    response = session.get(analytics_url)
    print(f"GET /admin/analytics - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin analytics page accessible!")
        if "Analytics Dashboard" in response.text:
            print("✅ Analytics page content loading correctly!")
        else:
            print("❌ Analytics page content issue")
    else:
        print("❌ Admin analytics page not accessible")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
