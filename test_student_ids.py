from app import app, db, Student, User

# Check actual student user IDs
with app.app_context():
    print("All users:")
    users = User.query.all()
    for user in users:
        print(f"  {user.username} (ID: {user.id}) - Role: {user.role}")
    
    print("\nAll students:")
    students = Student.query.all()
    for student in students:
        print(f"  Student ID {student.id} -> User ID {student.user_id} ({student.user.username})")
    
    print("\nTesting with correct student ID...")
    # Test with correct student ID (should be 4 based on our data)
    student = db.session.query(Student).filter_by(user_id=4).first()
    if student:
        print(f"✅ Found student: {student.user.username}")
        print(f"  Group: {student.group.name if student.group else 'None'}")
        if student.group:
            print(f"  Teacher: {student.group.teacher.user.full_name if student.group.teacher else 'None'}")
    else:
        print("❌ Student not found")
