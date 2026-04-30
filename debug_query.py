from app import app, db, Student, User, Group, Teacher, Course

with app.app_context():
    try:
        # Test simple query first
        students = Student.query.all()
        print(f"Simple Student query: {len(students)} students")
        
        # Test join with explicit conditions
        students_with_info = db.session.query(Student, User, Group, Teacher, User, Course)\
            .join(User, Student.user_id == User.id)\
            .join(Group, Student.group_id == Group.id)\
            .join(Teacher, Group.teacher_id == Teacher.id)\
            .join(User, Teacher.user_id == User.id)\
            .join(Course, Teacher.course_id == Course.id)\
            .limit(1)\
            .first()
        print("Complex query successful!")
        
    except Exception as e:
        print(f"Query error: {e}")
        import traceback
        traceback.print_exc()
