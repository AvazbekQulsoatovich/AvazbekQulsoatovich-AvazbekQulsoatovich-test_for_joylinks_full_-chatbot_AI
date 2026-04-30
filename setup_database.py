#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Teacher, Student, Course, Group, Test, Question, TestResult, Branch
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def setup_database():
    with app.app_context():
        db.create_all()
        print("🗑️  Bazani tozalash...")
        
        # Barcha ma'lumotlarni o'chirish, faqat adminni qoldirish
        TestResult.query.delete()
        Question.query.delete()
        Test.query.delete()
        Student.query.delete()
        Group.query.delete()
        Teacher.query.delete()
        Course.query.delete()
        Branch.query.delete()
        
        # Admin dan tashqari barcha userlarni o'chirish
        User.query.filter(User.role != 'admin').delete()
        
        db.session.commit()
        print("✅ Baza tozalandi!")
        
        # Branch yaratish
        default_branch = Branch(name="Toshkent")
        db.session.add(default_branch)
        db.session.commit()
        print(f"✅ Filial yaratildi: {default_branch.name}")

        # Admin ma'lumotlari
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('secure_admin_password_2024'),
                role='admin',
                full_name='Super Admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Yangi admin yaratildi!")
        
        # Adminni filialga biriktirish (ixtiyoriy, lekin yaxshi)
        admin.branch_id = None # Superadmin filialga bog'lanmagan bo'lishi mumkin
        db.session.commit()
        
        print(f"👑 Admin: {admin.username} | Parol: secure_admin_password_2024")
        
        print("\n📚 Kurslar yaratilmoqda...")
        # Kurslar yaratish
        courses_data = [
            {"name": "Kompyuter savodxonligi", "description": "Asosiy kompyuter ko'nikmalari"},
            {"name": "Frontend dasturlash", "description": "HTML, CSS, JavaScript va zamonaviy frameworklar"},
            {"name": "Backend dasturlash", "description": "Server tomoni dasturlash va ma'lumotlar bazasi"},
            {"name": "Ingliz tili", "description": "Professional ingliz tili kursi"}
        ]
        
        courses = []
        for course_data in courses_data:
            course = Course(
                name=course_data["name"], 
                description=course_data["description"],
                branch_id=default_branch.id
            )
            db.session.add(course)
            courses.append(course)
        
        db.session.commit()
        print(f"✅ {len(courses)} ta kurs yaratildi!")
        
        print("\n👨‍🏫 O'qituvchilar yaratilmoqda...")
        # O'qituvchilar yaratish
        teachers_data = [
            {"username": "teacher1", "password": "teacher123", "full_name": "Aliyev Karim", "course_idx": 0},
            {"username": "teacher2", "password": "teacher123", "full_name": "Saidova Dilnoza", "course_idx": 1},
            {"username": "teacher3", "password": "teacher123", "full_name": "Rahimov Botir", "course_idx": 2},
            {"username": "teacher4", "password": "teacher123", "full_name": "Hoshimova Gulnora", "course_idx": 3}
        ]
        
        teachers = []
        for i, teacher_data in enumerate(teachers_data):
            user = User(
                username=teacher_data["username"],
                password_hash=generate_password_hash(teacher_data["password"]),
                role="teacher",
                full_name=teacher_data["full_name"],
                branch_id=default_branch.id
            )
            db.session.add(user)
            db.session.flush()
            
            teacher = Teacher(
                user_id=user.id,
                course_id=courses[teacher_data["course_idx"]].id
            )
            db.session.add(teacher)
            teachers.append(teacher)
            
            print(f"   👨‍🏫 {teacher_data['full_name']} | Login: {teacher_data['username']} | Parol: {teacher_data['password']}")
        
        db.session.commit()
        print(f"✅ {len(teachers)} ta o'qituvchi yaratildi!")
        
        print("\n👥 Guruhlar yaratilmoqda...")
        # Guruhlar yaratish
        groups = []
        group_names = {
            "Kompyuter savodxonligi": ["A guruh", "B guruh"],
            "Frontend dasturlash": ["React guruh", "Vue guruh"],
            "Backend dasturlash": ["Python guruh", "Node.js guruh"],
            "Ingliz tili": ["Beginner guruh", "Advanced guruh"]
        }
        
        for course in courses:
            for group_name in group_names[course.name]:
                # Har bir kurs uchun tegishli o'qituvchini topish
                teacher = next(t for t in teachers if t.course_id == course.id)
                
                group = Group(
                    name=f"{course.name} - {group_name}",
                    teacher_id=teacher.id,
                    branch_id=default_branch.id
                )
                db.session.add(group)
                groups.append(group)
        
        db.session.commit()
        print(f"✅ {len(groups)} ta guruh yaratildi!")
        
        print("\n👨‍🎓 O'quvchilar qo'shilmoqda...")
        # O'quvchilar qo'shish
        students_info = []
        for i, group in enumerate(groups):
            for j in range(10):
                student_num = i * 10 + j + 1
                username = f"student{student_num:02d}"
                password = f"student{student_num:02d}"
                full_name = f"O'quvchi {student_num}"
                
                user = User(
                    username=username,
                    password_hash=generate_password_hash(password),
                    role="student",
                    full_name=full_name,
                    branch_id=default_branch.id
                )
                db.session.add(user)
                db.session.flush()
                
                student = Student(
                    user_id=user.id,
                    group_id=group.id
                )
                db.session.add(student)
                
                students_info.append({
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                    "group": group.name
                })
        
        db.session.commit()
        print(f"✅ {len(students_info)} ta o'quvchi qo'shildi!")
        
        print("\n📝 Testlar yaratilmoqda...")
        # Testlar yaratish
        test_questions = {
            "Kompyuter savodxonligi": [
                {"question": "Kompyuterning asosiy qurilmalari qaysilar?", "options": ["Monitor, klaviatura, sichqoncha", "Faqat monitor", "Faqat klaviatura", "Faqat sichqoncha"], "correct": "A"},
                {"question": "Windows nima?", "options": ["Operatsion sistema", "Dastur", "Fayl", "Papka"], "correct": "A"},
                {"question": "Internet nima?", "options": ["Global tarmoq", "Kompyuter", "Dastur", "Fayl"], "correct": "A"},
                {"question": "Email qanday ishlaydi?", "options": ["Xat yuborish orqali", "Telefon orqali", "SMS orqali", "Faks orqali"], "correct": "A"},
                {"question": "Virus nima?", "options": ["Zararli dastur", "Fayl", "Papka", "Dastur"], "correct": "A"}
            ],
            "Frontend dasturlash": [
                {"question": "HTML nima uchun ishlatiladi?", "options": ["Veb-sahifa tuzilishi", "Stil berish", "Interaktivlik", "Ma'lumotlar bazasi"], "correct": "A"},
                {"question": "CSS qanday ishlaydi?", "options": ["Stil berish", "Mantiq yozish", "Ma'lumot saqlash", "Server ishlashi"], "correct": "A"},
                {"question": "JavaScript nima?", "options": ["Dasturlash tili", "Stil tili", "Markup tili", "Database"], "correct": "A"},
                {"question": "React nima?", "options": ["JavaScript framework", "CSS framework", "Database", "Server"], "correct": "A"},
                {"question": "Responsive design nima?", "options": ["Har qanday ekranga moslash", "Faqat desktop", "Faqat mobile", "Faqat tablet"], "correct": "A"}
            ],
            "Backend dasturlash": [
                {"question": "Server nima?", "options": ["Ma'lumotlarni qayta ishlaydigan kompyuter", "Klient", "Browser", "Database"], "correct": "A"},
                {"question": "API nima?", "options": ["Dasturlar o'rtasidagi aloqa", "Database", "Frontend", "Backend"], "correct": "A"},
                {"question": "SQL nima?", "options": ["Database query tili", "Dasturlash tili", "Markup tili", "Stil tili"], "correct": "A"},
                {"question": "REST API nima?", "options": ["API arxitektura", "Database", "Framework", "Language"], "correct": "A"},
                {"question": "Authentication nima?", "options": ["Foydalanuvchini tasdiqlash", "Avtorizatsiya", "Validatsiya", "Enkripsiya"], "correct": "A"}
            ],
            "Ingliz tili": [
                {"question": "Hello'ning tarjimasi?", "options": ["Salom", "Xayr", "Rahmat", "Kechirasiz"], "correct": "A"},
                {"question": "Thank you'ning tarjimasi?", "options": ["Rahmat", "Salom", "Xayr", "Kechirasiz"], "correct": "A"},
                {"question": "Book nima?", "options": ["Kitob", "Daftar", "Ruchka", "Stol"], "correct": "A"},
                {"question": "Computer nima?", "options": ["Kompyuter", "Telefon", "Tablet", "Laptop"], "correct": "A"},
                {"question": "I am a student'ning tarjimasi?", "options": ["Men o'quvchiman", "Men o'qituvchiman", "Men ishlayman", "Men uqiman"], "correct": "A"}
            ]
        }
        
        tests = []
        for group in groups:
            course_name = group.name.split(" - ")[0]
            questions_data = test_questions[course_name]
            
            # Test yaratish
            test = Test(
                title=f"{course_name} - {group.name.split(' - ')[1]} testi",
                group_id=group.id,
                branch_id=default_branch.id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=30),
                duration_minutes=30
            )
            db.session.add(test)
            db.session.flush()
            
            # Savollar yaratish
            for i, q_data in enumerate(questions_data):
                question = Question(
                    test_id=test.id,
                    question_text=q_data["question"],
                    option_a=q_data["options"][0],
                    option_b=q_data["options"][1],
                    option_c=q_data["options"][2],
                    option_d=q_data["options"][3],
                    correct_answer=q_data["correct"]
                )
                db.session.add(question)
            
            tests.append(test)
        
        db.session.commit()
        print(f"✅ {len(tests)} ta test yaratildi!")
        
        print("\n🎉 Barcha ma'lumotlar muvaffaqiyatli yaratildi!")
        
        return {
            "admin": {"username": "admin", "password": "secure_admin_password_2024"},
            "teachers": teachers_data,
            "students": students_info[:10],  # Faqat birinchi 10 ta o'quvchi
            "total_students": len(students_info),
            "total_groups": len(groups),
            "total_tests": len(tests)
        }

if __name__ == "__main__":
    result = setup_database()
    
    print("\n" + "="*60)
    print("📋 LOGIN VA PAROLLAR")
    print("="*60)
    
    print(f"\n👑 ADMIN:")
    print(f"   Login: {result['admin']['username']}")
    print(f"   Parol: {result['admin']['password']}")
    
    print(f"\n👨‍🏫 O'QITUVCHILAR:")
    for teacher in result['teachers']:
        print(f"   {teacher['full_name']}: {teacher['username']} / {teacher['password']}")
    
    print(f"\n👨‍🎓 O'QUVCHILAR (birinchi 10 ta):")
    for student in result['students']:
        print(f"   {student['full_name']}: {student['username']} / {student['password']} ({student['group']})")
    
    print(f"\n📊 STATISTIKA:")
    print(f"   Jami o'quvchilar: {result['total_students']}")
    print(f"   Jami guruhlar: {result['total_groups']}")
    print(f"   Jami testlar: {result['total_tests']}")
    
    print("\n" + "="*60)
    print("✅ Tizim deploy uchun tayyor!")
    print("="*60)
