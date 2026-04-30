import requests

# Direct route test
session = requests.Session()

print("=== TO'G'RIDAN-TO'G'RI ROUTE TEST ===")
print()

# Login as aziz
login_data = {
    'username': 'aziz',
    'password': 'aziz'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Try different submit methods
    submit_data = {'question_3': 'A'}
    
    # Method 1: POST with form data
    print("Method 1: POST with form data")
    response1 = session.post('http://127.0.0.1:5000/student/test/3/submit', data=submit_data)
    print(f"Status: {response1.status_code}")
    print(f"Headers: {dict(response1.headers)}")
    
    # Method 2: POST with JSON
    print("\nMethod 2: POST with JSON")
    response2 = session.post('http://127.0.0.1:5000/student/test/3/submit', json=submit_data)
    print(f"Status: {response2.status_code}")
    
    # Method 3: GET (should fail)
    print("\nMethod 3: GET (should fail)")
    response3 = session.get('http://127.0.0.1:5000/student/test/3/submit')
    print(f"Status: {response3.status_code}")
    
    # Method 4: POST without data
    print("\nMethod 4: POST without data")
    response4 = session.post('http://127.0.0.1:5000/student/test/3/submit')
    print(f"Status: {response4.status_code}")
    
    # Check if any method worked
    if response1.status_code == 302 or response2.status_code == 302:
        print("\n✅ Route is working!")
    else:
        print("\n❌ Route not working properly")
        
        # Show response content
        print("\nResponse content:")
        print(response1.text[:500])
else:
    print("❌ Login xato")
