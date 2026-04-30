import requests
import sys

# Test afruz student login
login_url = 'http://127.0.0.1:5000/login'

try:
    session = requests.Session()
    
    # Test afruz login
    print("Testing afruz student login...")
    login_data = {
        'username': 'afruz',
        'password': 'afruz123'
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Afruz login response: {response.status_code}")
    
    if response.status_code == 302:
        print(f"✅ Login successful, redirecting to: {response.headers.get('Location')}")
        
        # Follow redirect to dashboard
        dashboard_url = response.headers.get('Location')
        if not dashboard_url.startswith('http'):
            dashboard_url = 'http://127.0.0.1:5000' + dashboard_url
        
        response = session.get(dashboard_url)
        print(f"Student dashboard: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Student dashboard accessible!")
            if "afruz" in response.text:
                print("✅ Student name found in dashboard!")
            else:
                print("❌ Student name not found in dashboard")
        else:
            print("❌ Student dashboard not accessible")
    else:
        print("❌ Login failed")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
