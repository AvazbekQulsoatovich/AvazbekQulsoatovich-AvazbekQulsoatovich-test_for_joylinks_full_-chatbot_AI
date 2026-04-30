import requests
import sys

# Test login route
url = 'http://127.0.0.1:5000/login'

try:
    # Test GET request
    response = requests.get(url)
    print(f"GET /login - Status: {response.status_code}")
    
    # Test POST request with correct credentials
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = requests.post(url, data=login_data, allow_redirects=False)
    print(f"POST /login (correct) - Status: {response.status_code}")
    print(f"Location header: {response.headers.get('Location', 'None')}")
    
    # Test POST request with wrong credentials
    wrong_data = {
        'username': 'admin',
        'password': 'wrong'
    }
    response = requests.post(url, data=wrong_data, allow_redirects=False)
    print(f"POST /login (wrong) - Status: {response.status_code}")
    
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Flask application!")
    print("Make sure the application is running on http://127.0.0.1:5000")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
