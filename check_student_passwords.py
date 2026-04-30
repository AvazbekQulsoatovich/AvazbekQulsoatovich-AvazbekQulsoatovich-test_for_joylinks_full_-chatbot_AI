from app import app, db, User, Student
from werkzeug.security import check_password_hash

with app.app_context():
    print("Checking all student login credentials:")
    
    # Get all student users
    student_users = User.query.filter_by(role='student').all()
    
    for user in student_users:
        print(f"\n👤 Student: {user.full_name}")
        print(f"   Username: {user.username}")
        
        # Try common passwords
        common_passwords = ['student123', 'password', '123456', user.username, user.full_name.lower().replace(' ', '')]
        
        found_password = False
        for password in common_passwords:
            if check_password_hash(user.password_hash, password):
                print(f"   ✅ Password: {password}")
                found_password = True
                break
        
        if not found_password:
            print(f"   ❌ Password: Unknown (not in common list)")
            print(f"   🔍 Hash: {user.password_hash[:50]}...")
    
    print("\n" + "="*50)
    print("To test login, use these credentials:")
    print("✅ student1 / student123 (working)")
    print("❓ afruz / [unknown password] (need to check with teacher)")
