import requests

# Test teacher results page
session = requests.Session()

print("=== TEACHER RESULTS PAGE TEST ===")
print()

# Login as teacher (avazbek)
login_data = {
    'username': 'webdevaj',
    'password': 'webdevaj123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Teacher login successful!")
    
    # Get teacher results page
    results_response = session.get('http://127.0.0.1:5000/teacher/results')
    
    print(f"Results page status: {results_response.status_code}")
    
    if results_response.status_code == 200:
        print("✅ Teacher results page loaded successfully!")
        
        content = results_response.text
        
        # Check for key elements
        checks = [
            ("Total Results", "Total Results card"),
            ("Passed", "Passed card"),
            ("Failed", "Failed card"),
            ("Average Score", "Average Score card"),
            ("Test Results", "Results table"),
            ("afruz", "Student name"),
            ("100.0%", "Score percentage"),
        ]
        
        found = 0
        for check, description in checks:
            if check in content:
                print(f"✅ {description} topildi")
                found += 1
            else:
                print(f"❌ {description} topilmadi")
        
        if found >= 5:
            print("✅ Teacher results page to'liq ishlaydi!")
        else:
            print("❌ Teacher results page qisman ishlaydi")
            
    else:
        print(f"❌ Results page xato: {results_response.status_code}")
        print("Error content:")
        print(results_response.text[:500])
else:
    print("❌ Teacher login xato")
