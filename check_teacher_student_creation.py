from app import app, db, User, Student, Group, Teacher
from werkzeug.security import check_password_hash

with app.app_context():
    print("Checking teacher-created students:")
    
    # Get all students and check their creation details
    students = Student.query.all()
    
    for student in students:
        user = User.query.get(student.user_id)
        group = Group.query.get(student.group_id)
        teacher = Teacher.query.get(group.teacher_id) if group else None
        teacher_user = User.query.get(teacher.user_id) if teacher else None
        
        print(f"\n👤 Student: {user.full_name}")
        print(f"   Username: {user.username}")
        print(f"   Created by: {teacher_user.full_name if teacher_user else 'Unknown'}")
        print(f"   Group: {group.name if group else 'None'}")
        
        # Test different password possibilities
        possible_passwords = [
            user.username,  # username as password
            user.username + '123',  # username + 123
            'password',  # default password
            '123456',  # simple password
            user.full_name.lower().replace(' ', ''),  # full name as password
        ]
        
        working_password = None
        for password in possible_passwords:
            if check_password_hash(user.password_hash, password):
                working_password = password
                break
        
        if working_password:
            print(f"   ✅ Working Password: {working_password}")
        else:
            print(f"   ❌ Password: Unknown (need to check with teacher)")
            print(f"   🔍 Hash: {user.password_hash[:50]}...")
    
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("Teachers should use consistent password patterns when creating students")
    print("Suggested patterns:")
    print("- username + 123 (e.g., 'afruz123')")
    print("- username alone (e.g., 'afruz')")
    print("- 'password' for all students")
