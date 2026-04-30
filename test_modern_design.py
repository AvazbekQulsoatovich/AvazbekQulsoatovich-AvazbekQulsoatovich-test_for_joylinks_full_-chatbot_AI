import requests

# Test modern design
session = requests.Session()

print("=== ZAMONAVIY DIZAYN TEST ===")
print()

# Test login page
login_response = session.get('http://127.0.0.1:5000/login')
print(f"Login page status: {login_response.status_code}")

if login_response.status_code == 200:
    print("✅ Login page loaded")
    
    # Check for modern elements
    content = login_response.text
    modern_elements = [
        ('gradient', 'Background gradient'),
        ('backdrop-filter', 'Glass effect'),
        ('border-radius: 20px', 'Rounded corners'),
        ('transition:', 'Smooth animations'),
        ('font-family: Inter', 'Modern font'),
    ]
    
    found = 0
    for element, description in modern_elements:
        if element in content:
            print(f"✅ {description}")
            found += 1
        else:
            print(f"❌ {description}")
    
    print(f"\nModern elements: {found}/{len(modern_elements)}")
else:
    print(f"❌ Login page error: {login_response.status_code}")

print("\n🎨 ZAMONAVIY DIZAYN XUSUSIYATLARI:")
print("1. 🌈 Gradient backgroundlar")
print("2. 🔲 Glass effect (backdrop-filter)")
print("3. 📐 Rounded corners (border-radius)")
print("4. ⚡ Smooth animations")
print("5. 🔤 Modern fonts (Inter)")
print("6. 📱 Responsive design")
print("7. 🎨 Custom CSS variables")
print("8. 💫 Hover effects")
print("9. 📊 Progress barlar")
print("10. 🎯 Card animations")
