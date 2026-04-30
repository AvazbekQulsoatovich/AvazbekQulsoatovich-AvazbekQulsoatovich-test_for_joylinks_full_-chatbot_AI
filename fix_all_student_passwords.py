from app import app, db, User, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Fixing all student passwords to consistent pattern (username + 123):")
    
    # Get all student users
    student_users = User.query.filter_by(role='student').all()
    
    fixed_count = 0
    for user in student_users:
        # Set password to username + 123
        new_password = user.username + '123'
        user.password_hash = generate_password_hash(new_password)
        
        print(f"✅ {user.full_name} ({user.username}) -> Password: {new_password}")
        fixed_count += 1
    
    # Commit all changes
    db.session.commit()
    
    print(f"\n🎉 Fixed {fixed_count} student passwords!")
    print("\n📝 All Student Login Credentials:")
    print("="*50)
    
    # Display all working credentials
    for user in student_users:
        print(f"✅ {user.username} / {user.username + '123'}")
        print(f"   Full Name: {user.full_name}")
    
    print(f"\n🎓 Now all students can log in with: username + '123'")
    print("Example: afruz -> afruz123, assi -> assi123, student1 -> student1123")
