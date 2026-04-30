import requests
import sys

# Test all student logins
login_url = 'http://127.0.0.1:5000/login'

students = [
    {'username': 'student1', 'password': 'student1123', 'name': 'Jane Student'},
    {'username': 'afruz', 'password': 'afruz123', 'name': 'afruz'},
    {'username': 'assi', 'password': 'assi123', 'name': 'asilbek'}
]

print("Testing all student logins:")
print("="*50)

all_passed = True

for student in students:
    try:
        session = requests.Session()
        
        # Test student login
        print(f"\n👤 Testing {student['name']} ({student['username']}):")
        
        login_data = {
            'username': student['username'],
            'password': student['password']
        }
        response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"   ✅ Login successful! Redirecting to: {redirect_url}")
            
            # Test dashboard access
            if redirect_url == '/student/dashboard':
                dashboard_response = session.get('http://127.0.0.1:5000' + redirect_url)
                if dashboard_response.status_code == 200:
                    print(f"   ✅ Dashboard accessible!")
                else:
                    print(f"   ❌ Dashboard not accessible ({dashboard_response.status_code})")
                    all_passed = False
        else:
            print(f"   ❌ Login failed ({response.status_code})")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False

print("\n" + "="*50)
if all_passed:
    print("🎉 ALL STUDENT LOGINS WORKING!")
else:
    print("❌ Some student logins failed")

print("\n📝 Final Student Credentials:")
for student in students:
    print(f"✅ {student['username']} / {student['password']}")
