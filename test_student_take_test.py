import requests
import sys

# Test student take test functionality
login_url = 'http://127.0.0.1:5000/login'

# Test afruz student
session = requests.Session()

print("=== TESTNI BOSHLASH TESTI ===")
print()

# Login as afruz
login_data = {
    'username': 'afruz',
    'password': 'afruz123'
}

response = session.post(login_url, data=login_data, allow_redirects=False)
print(f"Login status: {response.status_code}")

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Get dashboard
    dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
    content = dashboard_response.text
    
    # Find test link
    if "Take Test" in content:
        print("✅ 'Take Test' tugmasi topildi!")
        
        # Extract test ID from the link
        import re
        test_links = re.findall(r'href="/student/test/(\d+)"', content)
        
        if test_links:
            test_id = test_links[0]
            print(f"📝 Test ID: {test_id}")
            
            # Try to take the test
            test_url = f'http://127.0.0.1:5000/student/test/{test_id}'
            test_response = session.get(test_url)
            
            print(f"Test page status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("✅ Test page yuklandi!")
                
                # Check for test content
                test_content = test_response.text
                if "form" in test_content and "question" in test_content.lower():
                    print("✅ Test formasi topildi!")
                elif "has not started yet" in test_content.lower():
                    print("⏰ Test hali boshlanmadi - xabari ko'rsatiladi")
                elif "expired" in test_content.lower():
                    print("⏰ Test tugagan - xabari ko'rsatiladi")
                else:
                    print("❌ Test tarkibi topilmadi")
                    print("Content preview:")
                    print(test_content[:500])
            else:
                print(f"❌ Test page xato: {test_response.status_code}")
                print("Error content:")
                print(test_response.text[:500])
        else:
            print("❌ Test link topilmadi")
    else:
        print("❌ 'Take Test' tugmasi topilmadi")
else:
    print("❌ Login xato")
