import os
from app import app, db, Branch, User, Teacher, Student, Group, Course, Test, Question, TestResult
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def reset_database():
    print("🗑️ DATABASE RESET STARTING...")
    
    # 1. Drop existing DB
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'joylinks_test.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), 'joylinks_test.db')
    
    # Clean recreate
    db.drop_all()
    db.create_all()
    print("✅ All tables recreated with branch support")
    
    # 2. Create Super Admin
    super_admin = User(
        username='superadmin',
        password_hash=generate_password_hash('super123'),
        role='superadmin',
        full_name='Bosh Boshqaruvchi',
        branch_id=None
    )
    db.session.add(super_admin)
    db.session.commit()
    print("👑 Super Admin created: superadmin / super123")

    # 3. Create Branches
    branches_data = ['Joylinks Toshkent', 'Joylinks Samarqand', 'Joylinks Termiz']
    branches = []
    for b_name in branches_data:
        branch = Branch(name=b_name)
        db.session.add(branch)
        db.session.commit()
        branches.append(branch)
        print(f"🏢 Branch created: {b_name}")

    # Names for teachers and students
    first_names = ["Ali", "Vali", "Hasan", "Husan", "Madina", "Malika", "Zarina", "Sardor", "Rustam", "Jasur", "Anvar", "Dilshod"]
    last_names = ["Aliyev", "Valiyev", "Hasanov", "Husanov", "Nazarova", "Karimova", "Tolipova", "Umarov", "Sattorov", "Jabborov"]
    course_list = [("Ingliz tili", "Ayls"), ("IT Dasturlash", "Python"), ("Matematika", "Kalkulus")]

    # 4. Generate Branch specific data
    for i, branch in enumerate(branches):
        prefix = branch.name.split(' ')[1].lower() # toshkent, samarqand, termiz

        # Branch Admin
        admin = User(
            username=f'admin_{prefix}',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name=f'{branch.name} Admini',
            branch_id=branch.id
        )
        db.session.add(admin)
        db.session.commit()
        print(f"👔 Branch Admin created: admin_{prefix} / admin123")

        # Courses
        branch_courses = []
        for c_name, c_desc in course_list:
            course = Course(name=f"{c_name} ({branch.name})", description=c_desc, branch_id=branch.id)
            db.session.add(course)
            db.session.commit()
            branch_courses.append(course)
            
        # Teachers (3 per branch)
        branch_teachers = []
        for j in range(3):
            t_user = User(
                username=f'teacher_{prefix}_{j+1}',
                password_hash=generate_password_hash('teacher123'),
                role='teacher',
                full_name=f"{random.choice(first_names)} {random.choice(last_names)}",
                branch_id=branch.id
            )
            db.session.add(t_user)
            db.session.commit()

            teacher = Teacher(user_id=t_user.id, course_id=random.choice(branch_courses).id)
            db.session.add(teacher)
            db.session.commit()
            branch_teachers.append((t_user, teacher))
        
        # Groups and Students
        for t_user, teacher in branch_teachers:
            # 2 groups per teacher
            for k in range(2):
                group = Group(
                    name=f"{prefix[:3].upper()}-G{teacher.id}-{k+1}",
                    teacher_id=teacher.id,
                    branch_id=branch.id
                )
                db.session.add(group)
                db.session.commit()

                # Students (5 per group)
                students = []
                for s in range(5):
                    s_user = User(
                        username=f'stu_{prefix}_{group.id}_{s+1}',
                        password_hash=generate_password_hash('stu123'),
                        role='student',
                        full_name=f"{random.choice(first_names)} {random.choice(last_names)}",
                        branch_id=branch.id
                    )
                    db.session.add(s_user)
                    db.session.commit()

                    student = Student(user_id=s_user.id, group_id=group.id)
                    db.session.add(student)
                    db.session.commit()
                    students.append((s_user, student))

                # Create Tests
                test = Test(
                    title=f"{group.name} - Oylik Imtihon",
                    duration_minutes=60,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow() + timedelta(days=365),
                    group_id=group.id,
                    branch_id=branch.id
                )
                db.session.add(test)
                db.session.commit()

                # Test Results for students
                for s_user, student in students:
                    score = random.randint(30, 100)
                    res = TestResult(
                        student_id=student.id,
                        test_id=test.id,
                        score=score,
                        total_questions=100,
                        percentage=score,
                        submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    )
                    db.session.add(res)
                db.session.commit()

    print("✅ Dummy data population complete for multi-branches!")

if __name__ == '__main__':
    with app.app_context():
        reset_database()
