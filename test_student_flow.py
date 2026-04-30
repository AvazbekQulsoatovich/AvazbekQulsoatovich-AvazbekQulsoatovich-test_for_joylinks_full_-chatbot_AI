import requests
import sys

# Test complete student login flow
login_url = 'http://127.0.0.1:5000/login'

try:
    session = requests.Session()
    
    # Login as student
    print("Logging in as student...")
    login_data = {
        'username': 'student1',
        'password': 'student123'
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Student login response: {response.status_code}")
    
    if response.status_code == 302:
        # Follow redirect to dashboard
        dashboard_url = response.headers.get('Location')
        if not dashboard_url.startswith('http'):
            dashboard_url = 'http://127.0.0.1:5000' + dashboard_url
        print(f"Redirecting to: {dashboard_url}")
        
        response = session.get(dashboard_url)
        print(f"Student dashboard: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Student dashboard accessible!")
            if "Student Dashboard" in response.text:
                print("✅ Student dashboard content loading correctly!")
            else:
                print("❌ Student dashboard content issue")
                
            # Check for key content
            if "Jane Student" in response.text:
                print("✅ Student name found in dashboard!")
            if "CS101" in response.text:
                print("✅ Group name found in dashboard!")
            if "John Teacher" in response.text:
                print("✅ Teacher name found in dashboard!")
            if "Computer Science" in response.text:
                print("✅ Course name found in dashboard!")
        else:
            print("❌ Student dashboard not accessible")
    else:
        print("❌ Student login failed")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
