from app import app, db, Student, User
from werkzeug.security import check_password_hash

with app.app_context():
    try:
        # Test simple student query first
        print("Testing simple student query...")
        student_user = User.query.filter_by(username='student1').first()
        if student_user:
            print(f"✅ Student user found: {student_user.username}")
            
            # Test student relationship
            student = Student.query.filter_by(user_id=student_user.id).first()
            if student:
                print(f"✅ Student profile found: ID {student.id}")
                
                # Test accessing relationships
                try:
                    print(f"Student user: {student.user.username}")
                    print(f"Student group: {student.group.name if student.group else 'None'}")
                    if student.group:
                        print(f"Group teacher: {student.group.teacher.user.full_name if student.group.teacher else 'None'}")
                except Exception as e:
                    print(f"❌ Relationship access error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Student profile not found")
        else:
            print("❌ Student user not found")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        import traceback
        traceback.print_exc()
