import requests

# Test test page content
session = requests.Session()

# Login as afruz
login_data = {
    'username': 'afruz',
    'password': 'afruz123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    # Get test page
    test_response = session.get('http://127.0.0.1:5000/student/test/1')
    
    print("=== TEST PAGE CONTENT ===")
    content = test_response.text
    
    # Check for important elements
    checks = [
        ("form", "Test formasi"),
        ("question", "Savollar"),
        ("option", "Javob variantlari"),
        ("submit", "Yuborish tugmasi"),
        ("timer", "Timer"),
    ]
    
    for check, description in checks:
        if check in content.lower():
            print(f"✅ {description} topildi")
        else:
            print(f"❌ {description} topilmadi")
    
    # Show part of the content
    print("\n=== TEST PAGE PREVIEW ===")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'form' in line.lower() or 'question' in line.lower() or 'option' in line.lower():
            print(f"{i+1}: {line.strip()}")
            if i > 20:  # Limit output
                break
