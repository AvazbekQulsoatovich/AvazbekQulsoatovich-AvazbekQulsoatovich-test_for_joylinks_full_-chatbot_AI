from app import app, db, User, Student, Group, Teacher

with app.app_context():
    print("Checking all students in the system:")
    
    # Get all students
    students = Student.query.all()
    
    if not students:
        print("❌ No students found in the system!")
    else:
        print(f"✅ Found {len(students)} student(s):")
        for student in students:
            user = User.query.get(student.user_id)
            group = Group.query.get(student.group_id)
            teacher = Teacher.query.get(group.teacher_id) if group else None
            teacher_user = User.query.get(teacher.user_id) if teacher else None
            
            print(f"\n📚 Student: {user.full_name}")
            print(f"   Username: {user.username}")
            print(f"   Password: [Hashed]")
            print(f"   Group: {group.name if group else 'None'}")
            print(f"   Teacher: {teacher_user.full_name if teacher_user else 'None'}")
            print(f"   Created by: Teacher (not admin)")
    
    # Check if there are any students that might have been created by teachers
    print("\n" + "="*50)
    print("Testing login credentials:")
    
    # Test student1 login
    student_user = User.query.filter_by(username='student1').first()
    if student_user:
        print(f"✅ student1 user exists (ID: {student_user.id})")
        from werkzeug.security import check_password_hash
        if check_password_hash(student_user.password_hash, 'student123'):
            print("✅ Password 'student123' is correct")
        else:
            print("❌ Password 'student123' is incorrect")
    else:
        print("❌ student1 user not found")
