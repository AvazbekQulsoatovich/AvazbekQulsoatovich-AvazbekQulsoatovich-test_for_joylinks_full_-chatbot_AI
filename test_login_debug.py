import requests
import sys

# Debug login process
login_url = 'http://127.0.0.1:5000/login'

session = requests.Session()

# Test afruz login with detailed info
login_data = {
    'username': 'afruz',
    'password': 'afruz123'
}

print("=== LOGIN DEBUG ===")
print(f"Trying: {login_data['username']} / {login_data['password']}")

response = session.post(login_url, data=login_data, allow_redirects=False)
print(f"Response status: {response.status_code}")

if response.status_code == 302:
    print("✅ Login successful!")
    print(f"Redirect to: {response.headers.get('Location')}")
    
    # Follow redirect
    redirect_url = response.headers.get('Location')
    if not redirect_url.startswith('http'):
        redirect_url = 'http://127.0.0.1:5000' + redirect_url
    
    dashboard_response = session.get(redirect_url)
    print(f"Dashboard status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        content = dashboard_response.text
        if "afruz" in content:
            print("✅ Dashboard content loaded correctly!")
        else:
            print("⚠️ Dashboard loaded but content missing")
    else:
        print(f"❌ Dashboard failed: {dashboard_response.status_code}")
        
elif response.status_code == 200:
    print("❌ Login failed - returned to login page")
    if "Invalid username or password" in response.text:
        print("❌ Error: Invalid credentials")
    else:
        print("❌ Other login error")
else:
    print(f"❌ Unexpected status: {response.status_code}")

print("\n=== TESTING DIFFERENT PASSWORDS ===")
passwords_to_try = ['afruz123', 'afruz', 'password', '123456']

for password in passwords_to_try:
    test_session = requests.Session()
    test_response = test_session.post(login_url, data={
        'username': 'afruz',
        'password': password
    }, allow_redirects=False)
    
    if test_response.status_code == 302:
        print(f"✅ afruz / {password} - WORKS!")
        break
    else:
        print(f"❌ afruz / {password} - Failed")
