import requests
import sys

# Real web orqali student login test
login_url = 'http://127.0.0.1:5000/login'

students = [
    {'username': 'student1', 'password': 'student1123', 'name': 'Jane Student'},
    {'username': 'afruz', 'password': 'afruz123', 'name': 'afruz'},
    {'username': 'assi', 'password': 'assi123', 'name': 'asilbek'}
]

print("=== REAL WEB LOGIN TESTLARI ===")
print()

for i, student in enumerate(students, 1):
    print(f"{i}. {student['name']} ({student['username']}) login testi:")
    
    try:
        session = requests.Session()
        
        # Login urinishi
        login_data = {
            'username': student['username'],
            'password': student['password']
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"   ✅ Login muvaffaqiyatli! Redirect: {redirect_url}")
            
            # Dashboardga kirish testi
            if redirect_url == '/student/dashboard':
                dashboard_response = session.get('http://127.0.0.1:5000' + redirect_url)
                print(f"   Dashboard status: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    if student['name'] in dashboard_response.text or student['username'] in dashboard_response.text:
                        print(f"   ✅ Dashboard muvaffaqiyatli yuklandi!")
                    else:
                        print(f"   ⚠️ Dashboard yuklandi lekin ma'lumotlar yo'q")
                else:
                    print(f"   ❌ Dashboardga kirib bo'lmadi!")
            else:
                print(f"   ⚠️ Noto'g'ri redirect: {redirect_url}")
        else:
            print(f"   ❌ Login xato! Status: {response.status_code}")
            
            # Xato xabarni tekshirish
            if "Invalid username or password" in response.text:
                print(f"   ❌ Xato: Login yoki parol noto'g'ri")
            elif "Access denied" in response.text:
                print(f"   ❌ Xato: Ruxsat berilmadi")
            else:
                print(f"   ❌ Xato: Noma'lum xatolik")
        
    except Exception as e:
        print(f"   ❌ Connection xato: {e}")
    
    print()

print("=== XULOSA ===")
print("Agar barcha testlar ✅ belgisi bilan o'tsa, sistem to'liq ishlaydi.")
print("Agar ❌ belgisi bo'lsa, muammoni ko'rib chiqish kerak.")
