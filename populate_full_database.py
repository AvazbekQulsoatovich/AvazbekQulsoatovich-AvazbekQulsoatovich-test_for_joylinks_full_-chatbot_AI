"""
Comprehensive Database Population Script for Joylinks
Creates sample data for testing: Branches, Users, Courses, Teachers, Students, Tests, Results
"""

import sys
import os
import io

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.environ.setdefault('FLASK_APP', 'app.py')

from app import app, db, User, Branch, Course, Teacher, Group, Student, Test, Question, TestResult
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import json

def clear_database():
    """Clear all data from database"""
    print("🗑️  Tizimni tozalanmoqda...")
    db.drop_all()
    db.create_all()
    print("✅ Tizim tozalandi va qayta tuzildi")

def create_branches():
    """Create 2 branches"""
    print("\n📍 Filiallar yaratilmoqda...")
    
    branches = [
        Branch(name="Samarkand Filial"),
        Branch(name="Tashkent Filial")
    ]
    
    for branch in branches:
        db.session.add(branch)
    
    db.session.commit()
    print(f"✅ {len(branches)} ta filial yaratildi")
    return branches

def create_admins():
    """Create 2 admin users"""
    print("\n👨‍💼 Admin foydalanuvchilar yaratilmoqda...")
    
    admins = [
        User(
            username="admin_samarkand",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            full_name="Admin Samarkand",
            branch_id=1
        ),
        User(
            username="admin_tashkent",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            full_name="Admin Tashkent",
            branch_id=2
        )
    ]
    
    for admin in admins:
        db.session.add(admin)
    
    db.session.commit()
    print(f"✅ {len(admins)} ta admin yaratildi")
    return admins

def create_courses(branches):
    """Create 10 courses per branch"""
    print("\n📚 Kurslar yaratilmoqda...")
    
    course_names = [
        "Python Asoslari",
        "Web Development",
        "Database Design",
        "Mobile Apps",
        "Machine Learning",
        "Cloud Computing",
        "DevOps",
        "Cybersecurity",
        "Data Science",
        "Artificial Intelligence"
    ]
    
    courses = []
    for branch in branches:
        for i, name in enumerate(course_names):
            course = Course(
                name=name,
                description=f"{name} kursi - {branch.name}",
                branch_id=branch.id
            )
            courses.append(course)
            db.session.add(course)
    
    db.session.commit()
    print(f"✅ {len(courses)} ta kurs yaratildi")
    return courses

def create_teachers(branches, courses):
    """Create 10 teachers per branch"""
    print("\n👨‍🏫 O'qtuvchilar yaratilmoqda...")
    
    teachers_list = []
    user_count = 0
    
    for branch in branches:
        # Get courses for this branch
        branch_courses = [c for c in courses if c.branch_id == branch.id]
        
        for i in range(10):
            user_count += 1
            username = f"teacher_{branch.name.split()[0].lower()}_{i+1}"
            
            user = User(
                username=username,
                password_hash=generate_password_hash("teacher123"),
                role="teacher",
                full_name=f"O'qtuvchi {branch.name} - {i+1}",
                branch_id=branch.id
            )
            db.session.add(user)
            db.session.flush()  # Get the ID
            
            # Assign to a course from this branch
            course = branch_courses[i % len(branch_courses)]
            
            teacher = Teacher(
                user_id=user.id,
                course_id=course.id
            )
            db.session.add(teacher)
            teachers_list.append(teacher)
    
    db.session.commit()
    print(f"✅ {len(teachers_list)} ta o'qtuvchi yaratildi")
    return teachers_list

def create_groups(teachers):
    """Create groups for teachers"""
    print("\n👥 Guruhlar yaratilmoqda...")
    
    groups = []
    for teacher in teachers:
        for i in range(5):
            group = Group(
                name=f"Guruh-{teacher.id}-{i+1}",
                teacher_id=teacher.id,
                branch_id=teacher.course.branch_id
            )
            groups.append(group)
            db.session.add(group)
    
    db.session.commit()
    print(f"✅ {len(groups)} ta guruh yaratildi")
    return groups

def create_students(branches, groups):
    """Create 100 students per branch"""
    print("\n👨‍🎓 O'quvchilar yaratilmoqda...")
    
    students_list = []
    user_count = 0
    students_per_branch = 100
    
    for branch_idx, branch in enumerate(branches):
        # Get groups for this branch
        branch_groups = [g for g in groups if g.branch_id == branch.id]
        
        for i in range(students_per_branch):
            user_count += 1
            username = f"student_{branch.name.split()[0].lower()}_{i+1}"
            
            user = User(
                username=username,
                password_hash=generate_password_hash("student123"),
                role="student",
                full_name=f"O'quvchi {branch.name} - {i+1}",
                branch_id=branch.id
            )
            db.session.add(user)
            db.session.flush()
            
            # Assign to a group
            group = random.choice(branch_groups)
            student = Student(
                user_id=user.id,
                group_id=group.id
            )
            db.session.add(student)
            students_list.append(student)
    
    db.session.commit()
    print(f"✅ {len(students_list)} ta o'quvchi yaratildi ({students_per_branch} ta filial uchun)")
    return students_list

def create_tests(groups):
    """Create tests for groups"""
    print("\n📝 Testlar yaratilmoqda...")
    
    test_subjects = [
        "Python Asoslari - Test 1",
        "Web Development - Test 1",
        "Database - Test 1",
        "Algoritmlar - Test 1",
        "Data Types - Test 1"
    ]
    
    tests_list = []
    
    for group in groups:
        # Create 2-3 tests per group
        num_tests = random.randint(2, 3)
        for t in range(num_tests):
            start_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            end_time = start_time + timedelta(hours=2)
            
            test = Test(
                title=f"{random.choice(test_subjects)} (Guruh {group.id})",
                description=f"Test for group {group.name}",
                duration_minutes=120,
                start_time=start_time,
                end_time=end_time,
                group_id=group.id,
                branch_id=group.branch_id,
                is_active=random.choice([True, False])
            )
            db.session.add(test)
            db.session.flush()
            
            # Create 10 questions per test
            for q in range(10):
                question = Question(
                    test_id=test.id,
                    question_text=f"Savol {q+1}: Bu test uchun {q+1}-chi savol nima?",
                    option_a="Javob A",
                    option_b="Javob B",
                    option_c="To'g'ri javob",
                    option_d="Javob D",
                    correct_answer=random.choice(['A', 'B', 'C', 'D'])
                )
                db.session.add(question)
            
            tests_list.append(test)
    
    db.session.commit()
    print(f"✅ {len(tests_list)} ta test va {len(tests_list) * 10} ta savol yaratildi")
    return tests_list

def create_test_results(students_list, tests_list):
    """Create test results for students"""
    print("\n📊 Test natijalari yaratilmoqda...")
    
    results_list = []
    
    for student in students_list:
        # Each student takes 3-5 tests
        num_tests = random.randint(3, 5)
        available_tests = [t for t in tests_list if t.group_id == student.group_id]
        
        if available_tests:
            selected_tests = random.sample(available_tests, min(num_tests, len(available_tests)))
            
            for test in selected_tests:
                # Generate random score
                correct_answers = random.randint(2, 9)
                total = 10
                percentage = (correct_answers / total) * 100
                
                # Create random answers
                answers = {}
                for q_idx in range(1, total + 1):
                    answers[str(q_idx)] = random.choice(['A', 'B', 'C', 'D'])
                
                result = TestResult(
                    student_id=student.id,
                    test_id=test.id,
                    score=correct_answers,
                    total_questions=total,
                    percentage=percentage,
                    submitted_at=test.end_time + timedelta(hours=random.randint(1, 24)),
                    answers=json.dumps(answers)
                )
                db.session.add(result)
                results_list.append(result)
    
    db.session.commit()
    print(f"✅ {len(results_list)} ta test natijasi yaratildi")
    return results_list

def populate_database():
    """Main function to populate everything"""
    with app.app_context():
        print("=" * 60)
        print("🚀 Joylinks Ma'lumotlar Bazasini To'ldirish Boshlandi")
        print("=" * 60)
        
        # Clear existing data
        clear_database()
        
        # Create main entities
        branches = create_branches()
        admins = create_admins()
        courses = create_courses(branches)
        teachers = create_teachers(branches, courses)
        groups = create_groups(teachers)
        students = create_students(branches, groups)
        tests = create_tests(groups)
        results = create_test_results(students, tests)
        
        print("\n" + "=" * 60)
        print("📊 UMUMIY STATISTIKA")
        print("=" * 60)
        print(f"✅ Filiallar: {len(branches)}")
        print(f"✅ Adminlar: {len(admins)}")
        print(f"✅ Kurslar: {len(courses)}")
        print(f"✅ O'qtuvchilar: {len(teachers)}")
        print(f"✅ Guruhlar: {len(groups)}")
        print(f"✅ O'quvchilar: {len(students)}")
        print(f"✅ Testlar: {len(tests)}")
        print(f"✅ Test Natijalari: {len(results)}")
        
        # Print login credentials
        print("\n" + "=" * 60)
        print("🔐 LOGIN KALIT SO'ZLARI")
        print("=" * 60)
        
        print("\n👑 SUPERADMIN:")
        print("  Username: Avazbek")
        print("  Password: jumanazarov")
        
        print("\n👨‍💼 ADMIN FOYDALANUVCHILAR:")
        for admin in admins:
            print(f"  Username: {admin.username}")
            print(f"  Password: admin123")
            print(f"  Filial: {admin.branch.name}\n")
        
        # Get 2 teachers from each branch
        samarkand_teachers = Teacher.query.join(Teacher.course).filter(
            Course.branch_id == 1
        ).limit(2).all()
        tashkent_teachers = Teacher.query.join(Teacher.course).filter(
            Course.branch_id == 2
        ).limit(2).all()
        
        print("👨‍🏫 O'QTUVCHI FOYDALANUVCHILAR (2 ta har filialdan):")
        all_demo_teachers = samarkand_teachers + tashkent_teachers
        for teacher in all_demo_teachers:
            print(f"  Username: {teacher.user.username}")
            print(f"  Password: teacher123")
            print(f"  Rol: {teacher.user.role}")
            print(f"  Filial: {teacher.user.branch.name}\n")
        
        # Get 2 students from each branch
        samarkand_students = Student.query.join(Student.user).filter(
            User.branch_id == 1
        ).limit(2).all()
        tashkent_students = Student.query.join(Student.user).filter(
            User.branch_id == 2
        ).limit(2).all()
        
        print("👨‍🎓 O'QUVCHI FOYDALANUVCHILAR (2 ta har filialdan):")
        all_demo_students = samarkand_students + tashkent_students
        for student in all_demo_students:
            print(f"  Username: {student.user.username}")
            print(f"  Password: student123")
            print(f"  Guruh: {student.group.name}")
            print(f"  Filial: {student.user.branch.name}\n")
        
        print("=" * 60)
        print("✨ MA'LUMOTLAR BAZASI MUVAFFAQIYATLI TO'LDIRILDI!")
        print("=" * 60)

if __name__ == '__main__':
    populate_database()
