import requests
import sys

# Test student login process
login_url = 'http://127.0.0.1:5000/login'

try:
    session = requests.Session()
    
    # Test student login
    print("Testing student login...")
    login_data = {
        'username': 'student1',
        'password': 'student123'
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Student login response: {response.status_code}")
    
    if response.status_code == 302:
        print(f"✅ Login successful, redirecting to: {response.headers.get('Location')}")
    elif response.status_code == 200:
        print("❌ Login failed - returned to login page")
        # Check for error messages
        if "Invalid username or password" in response.text:
            print("❌ Error: Invalid username or password")
        elif "Access denied" in response.text:
            print("❌ Error: Access denied")
        else:
            print("❌ Unknown error occurred")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
