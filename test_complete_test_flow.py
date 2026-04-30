import requests
import sys

# Complete test flow test
session = requests.Session()

print("=== TO'LIQ TEST ISHLASH TESTI ===")
print()

# Login as afruz
login_data = {
    'username': 'afruz',
    'password': 'afruz123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Get test page
    test_response = session.get('http://127.0.0.1:5000/student/test/1')
    
    if test_response.status_code == 200:
        print("✅ Test page loaded!")
        
        content = test_response.text
        
        # Check for specific elements
        checks = [
            ("kim qachon edi", "Savol matni"),
            ("knskasn", "A variant"),
            ("sdljd", "B variant"),
            ("naksnakskndk", "C variant"),
            ("sjdsdjl", "D variant"),
            ("submit", "Yuborish tugmasi"),
        ]
        
        found_elements = 0
        for check, description in checks:
            if check in content:
                print(f"✅ {description} topildi")
                found_elements += 1
            else:
                print(f"❌ {description} topilmadi")
        
        if found_elements >= 5:
            print("✅ Test to'liq yuklandi!")
            
            # Try to submit the test
            submit_data = {
                'question_1': 'A'  # Choose option A
            }
            
            submit_response = session.post('http://127.0.0.1:5000/student/test/1/submit', data=submit_data)
            
            print(f"Submit status: {submit_response.status_code}")
            
            if submit_response.status_code == 302:
                print("✅ Test muvaffaqiyatli topshirildi!")
                
                # Check dashboard for results
                dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
                dashboard_content = dashboard_response.text
                
                if "Test submitted!" in dashboard_content:
                    print("✅ Natija xabari ko'rsatiladi!")
                if "100%" in dashboard_content or "0%" in dashboard_content:
                    print("✅ Natija foizi ko'rsatiladi!")
                    
            else:
                print(f"❌ Test topshirish xato: {submit_response.status_code}")
                print("Error content:")
                print(submit_response.text[:500])
        else:
            print("❌ Test to'liq yuklanmadi")
    else:
        print(f"❌ Test page xato: {test_response.status_code}")
else:
    print("❌ Login xato")
