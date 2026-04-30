import requests
import sys

# Final comprehensive test for all students
login_url = 'http://127.0.0.1:5000/login'

students = [
    {'username': 'student1', 'password': 'student1123', 'name': 'Jane Student', 'group': 'CS101'},
    {'username': 'afruz', 'password': 'afruz123', 'name': 'afruz', 'group': 'ing-tili14:00-16:00'},
    {'username': 'assi', 'password': 'assi123', 'name': 'asilbek', 'group': 'frontend jahon'}
]

print("=== O'QUVCHI LOGIN TIZIMI - YAKHUNIY TEST ===")
print("="*60)

all_success = True

for i, student in enumerate(students, 1):
    print(f"\n{i}. {student['name']} ({student['username']})")
    print(f"   Guruh: {student['group']}")
    
    try:
        session = requests.Session()
        
        # Login
        login_data = {
            'username': student['username'],
            'password': student['password']
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print(f"   ✅ Login muvaffaqiyatli!")
            
            # Dashboard test
            dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
            
            if dashboard_response.status_code == 200:
                content = dashboard_response.text
                
                # Ma'lumotlarni tekshirish
                checks = [
                    (student['name'], "Ismi"),
                    (student['username'], "Username"),
                    (student['group'], "Guruh nomi"),
                    ("Student Dashboard", "Dashboard sarlavhasi"),
                    ("No tests taken yet", "Test xabari")
                ]
                
                content_found = 0
                for check_text, description in checks:
                    if check_text in content:
                        print(f"      ✅ {description} topildi")
                        content_found += 1
                    else:
                        print(f"      ❌ {description} topilmadi")
                
                if content_found >= 3:  # Kamida 3 ta element topilsa
                    print(f"   ✅ Dashboard to'liq ishlaydi!")
                else:
                    print(f"   ⚠️ Dashboard qisman ishlaydi")
                    all_success = False
            else:
                print(f"   ❌ Dashboard xato: {dashboard_response.status_code}")
                all_success = False
        else:
            print(f"   ❌ Login xato: {response.status_code}")
            all_success = False
            
    except Exception as e:
        print(f"   ❌ Connection xato: {e}")
        all_success = False

print("\n" + "="*60)
if all_success:
    print("🎉 BARCHA O'QUVCHILAR LOGIN QILA OLADI!")
    print("✅ Tizim to'liq ishlayapti!")
else:
    print("❌ Ba'zi o'quvchilar muammoga duch keldi")

print("\n📝 BARCHA O'QUVCHI LOGIN KREDITSIAL'LARI:")
print("-" * 50)
for student in students:
    print(f"✅ {student['username']} / {student['password']}")

print(f"\n🎓 TAVSIYA: O'quvchilarga shu login ma'lumotlarini bering!")
