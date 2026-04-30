import requests

# Test with asilbek student
session = requests.Session()

print("=== ASILBEK BILAN TEST ===")
print()

# Login as asilbek
login_data = {
    'username': 'assi',
    'password': 'assi123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Get dashboard
    dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
    content = dashboard_response.text
    
    if "Take Test" in content:
        print("✅ 'Take Test' tugmasi topildi!")
        
        # Extract test ID
        import re
        test_links = re.findall(r'href="/student/test/(\d+)"', content)
        
        if test_links:
            test_id = test_links[0]
            print(f"📝 Test ID: {test_id}")
            
            # Get test page
            test_response = session.get(f'http://127.0.0.1:5000/student/test/{test_id}')
            
            print(f"Test page status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                test_content = test_response.text
                
                # Check for content
                checks = [
                    ("sdljsidskjdljkl", "Savol matni"),
                    ("sdjsjjjsod", "A variant"),
                    ("sdjohjhijdh", "B variant"),
                    ("mlkdjbssdjk", "C variant"),
                    ("ojhshvghidbhaj", "D variant"),
                ]
                
                found = 0
                for check, description in checks:
                    if check in test_content:
                        print(f"✅ {description} topildi")
                        found += 1
                    else:
                        print(f"❌ {description} topilmadi")
                
                if found >= 4:
                    print("✅ Test to'liq yuklandi!")
                    
                    # Submit test
                    submit_data = {'question_2': 'B'}  # Test ID 2, question ID 2
                    
                    submit_response = session.post(f'http://127.0.0.1:5000/student/test/{test_id}/submit', data=submit_data)
                    print(f"Submit status: {submit_response.status_code}")
                    
                    if submit_response.status_code == 302:
                        print("✅ Test topshirildi!")
                    else:
                        print(f"❌ Submit xato: {submit_response.status_code}")
                else:
                    print("❌ Test to'liq yuklanmadi")
            else:
                print(f"❌ Test page xato: {test_response.status_code}")
        else:
            print("❌ Test link topilmadi")
    else:
        print("❌ 'Take Test' tugmasi topilmadi")
else:
    print("❌ Login xato")
