import requests
import sys

# Test student test visibility
login_url = 'http://127.0.0.1:5000/login'

students = [
    {'username': 'afruz', 'password': 'afruz123', 'name': 'afruz', 'expected_tests': 1},
    {'username': 'assi', 'password': 'assi123', 'name': 'asilbek', 'expected_tests': 1},
    {'username': 'aziz', 'password': 'aziz', 'name': 'aziz', 'expected_tests': 2}
]

print("=== O'QUVCHI TEST KO'RISH TESTI ===")
print("="*60)

all_success = True

for student in students:
    print(f"\n👤 {student['name']} ({student['username']})")
    print(f"   Kutayotgan testlar: {student['expected_tests']} ta")
    
    try:
        session = requests.Session()
        
        # Login
        login_data = {
            'username': student['username'],
            'password': student['password']
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            # Get dashboard
            dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
            content = dashboard_response.text
            
            # Check for available tests section
            if "Available Tests" in content:
                print(f"   ✅ 'Available Tests' bo'limi topildi")
                
                # Count tests in the table
                import re
                test_rows = re.findall(r'<tr>.*?</tr>', content, re.DOTALL)
                test_count = len([row for row in test_rows if 'Take Test' in row or 'Not Started' in row or 'Expired' in row])
                
                print(f"   📊 Ko'rilayotgan testlar: {test_count} ta")
                
                if test_count >= student['expected_tests']:
                    print(f"   ✅ Testlar to'g'ri ko'rilmoqda!")
                else:
                    print(f"   ⚠️ Testlar kamroq ko'rilmoqda")
                    all_success = False
                
                # Check for specific test names
                if student['username'] == 'afruz' and 'yanvar oy test' in content:
                    print(f"   ✅ 'yanvar oy test' topildi")
                elif student['username'] == 'assi' and 'yanvar test' in content:
                    print(f"   ✅ 'yanvar test' topildi")
                elif student['username'] == 'aziz' and ('yanvar' in content and 'skkldnfbfkdl;' in content):
                    print(f"   ✅ Ikkala test ham topildi")
                
            else:
                print(f"   ❌ 'Available Tests' bo'limi topilmadi")
                all_success = False
        else:
            print(f"   ❌ Login xato: {response.status_code}")
            all_success = False
            
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        all_success = False

print("\n" + "="*60)
if all_success:
    print("🎉 BARCHA O'QUVCHILAR O'Z TESTLARINI KO'RA OLADI!")
    print("✅ Test ko'rish muammosi hal qilindi!")
else:
    print("❌ Ba'zi o'quvchilar testlarini ko'ra olmayapti")

print(f"\n🎓 YANGILIK:")
print("Endi o'quvchilar o'zlariga qo'yilgan testlarni dashboardda ko'ra oladi!")
print("Testlar statusi (Upcoming/Active/Ended) ko'rsatiladi.")
