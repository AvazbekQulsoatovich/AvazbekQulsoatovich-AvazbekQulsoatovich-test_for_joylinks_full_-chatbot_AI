import requests
import sys

# Test all system functions
session = requests.Session()

print("=== TIZIMNI TO'LIQ TEKSHIRISH ===")
print("="*60)

# Test data
users = [
    {'username': 'webdevaj', 'password': 'webdevaj123', 'role': 'teacher', 'name': 'Ustoz'},
    {'username': 'afruz', 'password': 'afruz123', 'role': 'student', 'name': 'O\'quvchi'},
    {'username': 'assi', 'password': 'assi123', 'role': 'student', 'name': 'O\'quvchi'},
]

functions_to_test = [
    {'name': 'Login', 'url': '/login', 'method': 'POST'},
    {'name': 'Dashboard', 'url': '/teacher/dashboard', 'method': 'GET'},
    {'name': 'Students', 'url': '/teacher/students', 'method': 'GET'},
    {'name': 'Tests', 'url': '/teacher/tests', 'method': 'GET'},
    {'name': 'Results', 'url': '/teacher/results', 'method': 'GET'},
    {'name': 'Student Dashboard', 'url': '/student/dashboard', 'method': 'GET'},
]

all_success = True

for user in users:
    print(f"\n👤 {user['name']} ({user['username']}) - {user['role']}")
    print("-" * 40)
    
    # Login
    login_response = session.post('http://127.0.0.1:5000/login', 
                             data={'username': user['username'], 'password': user['password']}, 
                             allow_redirects=False)
    
    if login_response.status_code == 302:
        print("✅ Login successful")
        
        # Test functions based on role
        if user['role'] == 'teacher':
            functions = functions_to_test[1:5]  # Teacher functions
        else:
            functions = [functions_to_test[5]]  # Student function
        
        for func in functions:
            try:
                response = session.get(f'http://127.0.0.1:5000{func["url"]}')
                
                if response.status_code == 200:
                    print(f"✅ {func['name']} - {response.status_code}")
                    
                    # Check for basic content
                    if func['name'] == 'Dashboard' and 'Dashboard' in response.text:
                        print("   📊 Dashboard content loaded")
                    elif func['name'] == 'Students' and 'Students' in response.text:
                        print("   👥 Students list loaded")
                    elif func['name'] == 'Tests' and 'Tests' in response.text:
                        print("   📝 Tests list loaded")
                    elif func['name'] == 'Results' and 'Results' in response.text:
                        print("   📈 Results loaded")
                    elif func['name'] == 'Student Dashboard' and 'Dashboard' in response.text:
                        print("   🎓 Student dashboard loaded")
                        
                else:
                    print(f"❌ {func['name']} - {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                print(f"❌ {func['name']} - Error: {e}")
                all_success = False
                
    else:
        print(f"❌ Login failed - {login_response.status_code}")
        all_success = False

print("\n" + "="*60)
if all_success:
    print("🎉 BARCHA FUNKSIYALAR ISHLAYDI!")
    print("✅ Tizim to'liq funksional")
else:
    print("❌ BA'ZI FUNKSIYALAR ISHLAMADI")

print(f"\n🎨 DIZAYN ZAMONIYLASHTIRISH UCHUN:")
print("1. Bootstrap 5 dan foydalanish")
print("2. Modern ranglar sxemasi")
print("3. Responsive dizayn")
print("4. Animatsiya va transition lar")
print("5. Icon lar (Font Awesome 6)")
print("6. Kartkalar va card lar")
print("7. Progress bar lar")
print("8. Modal oynalar")
