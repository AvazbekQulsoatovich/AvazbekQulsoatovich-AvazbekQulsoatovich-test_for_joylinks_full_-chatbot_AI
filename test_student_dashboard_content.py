import requests
import sys

# Student dashboard content test
login_url = 'http://127.0.0.1:5000/login'

# Test afruz student
session = requests.Session()
login_data = {
    'username': 'afruz',
    'password': 'afruz123'
}

response = session.post(login_url, data=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 302:
    # Get dashboard
    dashboard_response = session.get('http://127.0.0.1:5000/student/dashboard')
    print(f"Dashboard status: {dashboard_response.status_code}")
    
    # Check for specific content
    content = dashboard_response.text
    
    print("\n=== DASHBOARD CONTENT CHECK ===")
    
    # Check for student name
    if "afruz" in content:
        print("✅ Student name found: afruz")
    else:
        print("❌ Student name NOT found: afruz")
    
    # Check for group info
    if "ing-tili14:00-16:00" in content:
        print("✅ Group name found: ing-tili14:00-16:00")
    else:
        print("❌ Group name NOT found")
    
    # Check for teacher info
    if "avazbek" in content.lower():
        print("✅ Teacher name found: avazbek")
    else:
        print("❌ Teacher name NOT found")
    
    # Check for course info
    if "frontend" in content.lower():
        print("✅ Course name found: frontend")
    else:
        print("❌ Course name NOT found")
    
    # Check for "No tests taken yet" message
    if "No tests taken yet" in content:
        print("✅ 'No tests taken yet' message found")
    else:
        print("❌ 'No tests taken yet' message NOT found")
    
    print("\n=== SAMPLE CONTENT ===")
    print(content[:1000] + "..." if len(content) > 1000 else content)
