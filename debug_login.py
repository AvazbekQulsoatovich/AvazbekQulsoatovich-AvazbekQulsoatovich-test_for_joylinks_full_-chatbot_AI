import requests
import sys

# Debug login process
login_url = 'http://127.0.0.1:5000/login'

try:
    session = requests.Session()
    
    # Test admin login
    print("Testing admin login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Admin login response: {response.status_code}")
    if response.status_code == 302:
        print(f"Admin redirect to: {response.headers.get('Location')}")
    
    # Test teacher login
    print("\nTesting teacher login...")
    login_data = {
        'username': 'teacher1',
        'password': 'teacher123'
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Teacher login response: {response.status_code}")
    if response.status_code == 302:
        print(f"Teacher redirect to: {response.headers.get('Location')}")
    elif response.status_code == 200:
        print("Teacher login returned 200 - checking for errors...")
        print("Response content:")
        print(response.text[:500])  # First 500 chars
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
