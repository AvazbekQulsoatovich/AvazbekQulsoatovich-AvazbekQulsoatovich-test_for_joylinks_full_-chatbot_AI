import requests

# Direct test submit
session = requests.Session()

print("=== TO'G'RIDAN-TO'G'RI TEST SUBMIT ===")
print()

# Login as asilbek
login_data = {
    'username': 'assi',
    'password': 'assi123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Direct submit without getting test page
    submit_data = {
        'question_2': 'B'  # Test ID 2, question ID 2, answer B
    }
    
    submit_response = session.post('http://127.0.0.1:5000/student/test/2/submit', data=submit_data)
    
    print(f"Direct submit status: {submit_response.status_code}")
    
    if submit_response.status_code == 302:
        print("✅ Direct submit muvaffaqiyatli!")
        
        # Check dashboard
        dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
        dashboard_content = dashboard_response.text
        
        if "Test submitted!" in dashboard_content:
            print("✅ Natija xabari ko'rsatiladi!")
        if "100%" in dashboard_content:
            print("✅ 100% natija ko'rsatiladi!")
            
    elif submit_response.status_code == 200:
        print("❌ Submit 200 qaytardi - xatolik bor")
        print("Response content:")
        print(submit_response.text[:500])
    else:
        print(f"❌ Submit xato: {submit_response.status_code}")
else:
    print("❌ Login xato")
