from app import app, db, User, Course, Teacher, Group, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Create a course if not exists
    if not Course.query.filter_by(name='Computer Science').first():
        course = Course(name='Computer Science', description='Introduction to Computer Science')
        db.session.add(course)
        db.session.commit()
        print("Created Computer Science course")
    
    # Create a teacher if not exists
    if not User.query.filter_by(username='teacher1').first():
        # Create teacher user
        teacher_user = User(
            username='teacher1',
            password_hash=generate_password_hash('teacher123'),
            role='teacher',
            full_name='John Teacher'
        )
        db.session.add(teacher_user)
        db.session.flush()
        
        # Create teacher profile
        teacher = Teacher(user_id=teacher_user.id, course_id=course.id)
        db.session.add(teacher)
        db.session.commit()
        print("Created teacher1 user")
    
    # Create a group if not exists
    teacher = Teacher.query.filter_by(user_id=User.query.filter_by(username='teacher1').first().id).first()
    if not Group.query.filter_by(name='CS101').first():
        group = Group(name='CS101', teacher_id=teacher.id)
        db.session.add(group)
        db.session.commit()
        print("Created CS101 group")
    
    # Create a student if not exists
    if not User.query.filter_by(username='student1').first():
        # Create student user
        student_user = User(
            username='student1',
            password_hash=generate_password_hash('student123'),
            role='student',
            full_name='Jane Student'
        )
        db.session.add(student_user)
        db.session.flush()
        
        # Create student profile
        student = Student(user_id=student_user.id, group_id=group.id)
        db.session.add(student)
        db.session.commit()
        print("Created student1 user")
    
    print("Test data created successfully!")
    print("Login credentials:")
    print("Admin: admin / admin123")
    print("Teacher: teacher1 / teacher123")
    print("Student: student1 / student123")
