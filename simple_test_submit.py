import requests
import time

# Simple test submit
session = requests.Session()

print("=== ODDIY TEST SUBMIT ===")
print()

# Login as new student (aziz)
login_data = {
    'username': 'aziz',
    'password': 'aziz'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Check if aziz has tests
    dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
    dashboard_content = dashboard_response.text
    
    if "Take Test" in dashboard_content:
        print("✅ Azizda test bor!")
        
        # Extract test ID
        import re
        test_links = re.findall(r'href="/student/test/(\d+)"', dashboard_content)
        
        if test_links:
            test_id = test_links[0]
            print(f"📝 Test ID: {test_id}")
            
            # Get test page
            test_response = session.get(f'http://127.0.0.1:5000/student/test/{test_id}')
            
            if test_response.status_code == 200:
                print("✅ Test page yuklandi!")
                
                # Submit test
                submit_data = {f'question_{test_id}': 'A'}
                
                print("Testni topshirish...")
                submit_response = session.post(f'http://127.0.0.1:5000/student/test/{test_id}/submit', data=submit_data)
                
                print(f"Submit status: {submit_response.status_code}")
                
                if submit_response.status_code == 302:
                    print("✅ Test muvaffaqiyatli topshirildi!")
                    
                    # Check dashboard for results
                    final_dashboard = session.get('http://127.0.0.1:5000/student/dashboard')
                    
                    if "Test submitted!" in final_dashboard.text:
                        print("✅ Natija xabari ko'rsatiladi!")
                    
                    if "100%" in final_dashboard.text or "0%" in final_dashboard.text:
                        print("✅ Natija foizi ko'rsatiladi!")
                        
                elif submit_response.status_code == 200:
                    print("❌ Submit 200 qaytardi - xatolik bor")
                    print("Response preview:")
                    print(submit_response.text[:300])
                else:
                    print(f"❌ Submit xato: {submit_response.status_code}")
            else:
                print(f"❌ Test page xato: {test_response.status_code}")
        else:
            print("❌ Test link topilmadi")
    else:
        print("❌ Azizda test yo'q")
else:
    print("❌ Login xato")
