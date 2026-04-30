import random
from datetime import datetime, timedelta
from app import app, db, User, Course, Teacher, Group, Student, Test, Question, TestResult
from werkzeug.security import generate_password_hash

# List of sample names, courses, and texts for generation
first_names = ["Ali", "Vali", "Hasan", "Husan", "Madina", "Malika", "Zarina", "Sardor", "Rustam", "Jasur", "Anvar", "Dilshod", "Shahboz", "Nodir", "Umid", "Farruh", "Aziz", "Bekzod", "Sanjarg", "Tohir"]
last_names = ["Aliyev", "Valiyev", "Hasanov", "Husanov", "Nazarova", "Karimova", "Tolipova", "Umarov", "Sattorov", "Jabborov", "Rahimov", "Tursunov", "Zokirov", "Qodirov", "Olimov", "Mamatov", "Botirov", "Ismoilov"]

course_names = ["Matematika", "Fizika", "Ingliz tili", "Tarix", "Dasturlash", "Ona tili"]

with app.app_context():
    print("Dummy ma'lumotlarni yaratishni boshladik...")
    
    # 1. Create Courses
    courses = []
    for c_name in course_names:
        course = Course.query.filter_by(name=c_name).first()
        if not course:
            course = Course(name=c_name, description=f"{c_name} kursi bo'yicha asosiy darslar")
            db.session.add(course)
        courses.append(course)
    db.session.commit()
    print("Kurslar yaratildi.")

    # 2. Create 20 Teachers
    teachers = []
    for i in range(1, 21):
        username = f"ustoz_{i}"
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                password_hash=generate_password_hash('ustoz123'),
                role='teacher',
                full_name=f"{random.choice(first_names)} {random.choice(last_names)}"
            )
            db.session.add(user)
            db.session.flush()
            
            course = random.choice(courses)
            teacher = Teacher(user_id=user.id, course_id=course.id)
            db.session.add(teacher)
        else:
            teacher = Teacher.query.filter_by(user_id=user.id).first()
        teachers.append(teacher)
    db.session.commit()
    print("20 ta o'qituvchi yaratildi.")

    # 3. Create Groups (1-2 per teacher = ~30 groups)
    groups = []
    for i, t in enumerate(teachers, 1):
        g_name = f"Guruh-{100 + i}"
        group = Group.query.filter_by(name=g_name).first()
        if not group:
            group = Group(name=g_name, teacher_id=t.id)
            db.session.add(group)
        groups.append(group)
    db.session.commit()
    print("Guruhlar yaratildi.")

    # 4. Create 110 Students
    students = []
    for i in range(1, 111):
        username = f"oquvchi_{i}"
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                password_hash=generate_password_hash('oquvchi123'),
                role='student',
                full_name=f"{random.choice(first_names)} {random.choice(last_names)}"
            )
            db.session.add(user)
            db.session.flush()
            
            group = random.choice(groups)
            student = Student(user_id=user.id, group_id=group.id)
            db.session.add(student)
        else:
            student = Student.query.filter_by(user_id=user.id).first()
        students.append(student)
    db.session.commit()
    print("110 ta o'quvchi yaratildi.")

    # 5. Create Tests & Questions
    tests = []
    for group in groups:
        test = Test.query.filter_by(group_id=group.id).first()
        if not test:
            test = Test(
                title=f"{group.name} uchun Choraklik Test",
                description="Matematika va mantiq bo'yicha savollar",
                duration_minutes=30,
                start_time=datetime.utcnow() - timedelta(days=2),
                end_time=datetime.utcnow() + timedelta(days=5),
                group_id=group.id,
                is_active=True
            )
            db.session.add(test)
            db.session.flush()
            
            # Add 5 questions
            for j in range(1, 6):
                q = Question(
                    test_id=test.id,
                    question_text=f"{j}-savol: Ushbu formula qanday yechiladi?",
                    option_a="To'g'ri javob A",
                    option_b="Xato javob B",
                    option_c="Xato javob C",
                    option_d="Xato javob D",
                    correct_answer=random.choice(["A", "B", "C", "D"])
                )
                db.session.add(q)
        tests.append(test)
    db.session.commit()
    print("Testlar va savollar yaratildi.")

    # 6. Generate Test Results for students
    for student in students:
        # Check if already took test
        test = Test.query.filter_by(group_id=student.group_id).first()
        if not test: continue
        
        result = TestResult.query.filter_by(student_id=student.id, test_id=test.id).first()
        if not result:
            questions = Question.query.filter_by(test_id=test.id).all()
            correct_count = 0
            student_answers = {}
            for q in questions:
                # 60% chance to answer correctly
                if random.random() < 0.6:
                    ans = q.correct_answer
                    correct_count += 1
                else:
                    ans = random.choice([opt for opt in ["A", "B", "C", "D"] if opt != q.correct_answer])
                student_answers[str(q.id)] = ans
            
            pct = (correct_count / len(questions)) * 100
            
            result = TestResult(
                student_id=student.id,
                test_id=test.id,
                score=correct_count,
                total_questions=len(questions),
                percentage=pct,
                answers=str(student_answers),
                submitted_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            db.session.add(result)
            
    db.session.commit()
    print("O'quvchilar testlari ham avtomatik yaratildi!")
    
    print("-----------------------------------------")
    print("LOGIN PAROLLAR:")
    print("- O'qituvchilar: ustoz_1 dan ustoz_20 gacha. Parol: ustoz123")
    print("- O'quvchilar: oquvchi_1 dan oquvchi_110 gacha. Parol: oquvchi123")
    print("-----------------------------------------")
