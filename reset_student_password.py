from app import app, db, User, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    # Find the student 'afruz'
    student_user = User.query.filter_by(username='afruz').first()
    
    if student_user:
        print(f"Found student: {student_user.full_name} (username: {student_user.username})")
        
        # Reset password to 'afruz123' (username + 123)
        new_password = 'afruz123'
        student_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        print(f"✅ Password reset successfully!")
        print(f"📝 New login credentials:")
        print(f"   Username: {student_user.username}")
        print(f"   Password: {new_password}")
        print(f"   Full Name: {student_user.full_name}")
    else:
        print("❌ Student 'afruz' not found!")
    
    print("\n" + "="*50)
    print("All student login credentials:")
    
    # Show all working student credentials
    student_users = User.query.filter_by(role='student').all()
    for user in student_users:
        if user.username == 'student1':
            print(f"✅ {user.username} / student123")
        elif user.username == 'afruz':
            print(f"✅ {user.username} / afruz123 (newly reset)")
        else:
            print(f"❓ {user.username} / [unknown]")
