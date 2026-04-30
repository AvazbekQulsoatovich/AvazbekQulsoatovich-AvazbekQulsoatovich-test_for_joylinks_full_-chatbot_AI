from app import app, db, User, Student, TestResult, Test

with app.app_context():
    print("=== STUDENT DASHBOARD MA'LUMOTLARI TEKSHIRUVI ===")
    print()
    
    # Har bir o'quvchi uchun dashboard ma'lumotlarini tekshirish
    students = Student.query.all()
    
    for i, student in enumerate(students, 1):
        user = User.query.get(student.user_id)
        
        print(f"{i}. {user.full_name} ({user.username}) dashboard ma'lumotlari:")
        print(f"   Student ID: {student.id}")
        print(f"   User ID: {student.user_id}")
        print(f"   Group ID: {student.group_id}")
        
        # Guruh ma'lumotlari
        if student.group:
            print(f"   Guruh: {student.group.name}")
            if student.group.teacher:
                print(f"   Ustoz: {student.group.teacher.user.full_name}")
                if student.group.teacher.course:
                    print(f"   Kurs: {student.group.teacher.course.name}")
        else:
            print(f"   ❌ Guruh topilmadi!")
        
        # Test natijalari
        results = db.session.query(TestResult, Test).join(Test, TestResult.test_id == Test.id).filter(TestResult.student_id == student.id).order_by(TestResult.submitted_at.desc()).all()
        print(f"   Test natijalari: {len(results)} ta")
        
        for j, (result, test) in enumerate(results, 1):
            print(f"     {j}. {test.title} - {result.score}/{result.total_questions} ({result.percentage}%)")
        
        if not results:
            print(f"   ⚠️ Bu o'quvchi hali hech qanday test topshirmagan")
        
        print()
    
    print("=== TEMPLATE VARIABLE'LAR TEKSHIRUVI ===")
    
    # Birinchi o'quvchi uchun template ma'lumotlarini tekshirish
    if students:
        student = students[0]
        user = User.query.get(student.user_id)
        results = db.session.query(TestResult, Test).join(Test, TestResult.test_id == Test.id).filter(TestResult.student_id == student.id).order_by(TestResult.submitted_at.desc()).all()
        
        print(f"Templatega yuboriladigan ma'lumotlar:")
        print(f"student.user.full_name: {student.user.full_name}")
        print(f"student.user.username: {student.user.username}")
        print(f"student.group.name: {student.group.name if student.group else 'None'}")
        print(f"student.group.teacher.user.full_name: {student.group.teacher.user.full_name if student.group and student.group.teacher else 'None'}")
        print(f"student.group.teacher.course.name: {student.group.teacher.course.name if student.group and student.group.teacher and student.group.teacher.course else 'None'}")
        print(f"results count: {len(results)}")
