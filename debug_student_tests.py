from app import app, db, Student, Test, Group, Teacher, User

with app.app_context():
    print("=== O'QUVCHI TEST KO'RISH MUAMMOSI TEKSHIRUVI ===")
    print()
    
    # Barcha testlarni ko'rish
    tests = Test.query.all()
    print(f"Jami testlar soni: {len(tests)}")
    
    for test in tests:
        group = Group.query.get(test.group_id)
        teacher = Teacher.query.get(group.teacher_id) if group else None
        teacher_user = User.query.get(teacher.user_id) if teacher else None
        
        print(f"\n📝 TEST: {test.title}")
        print(f"   Guruh: {group.name if group else 'Noma\'lum'}")
        print(f"   Ustoz: {teacher_user.full_name if teacher_user else 'Noma\'lum'}")
        print(f"   Boshlanish: {test.start_time}")
        print(f"   Tugash: {test.end_time}")
        print(f"   Davomiyligi: {test.duration_minutes} daqiqa")
    
    print("\n" + "="*60)
    print("O'QUVCHILARNING TESTLARINI TEKSHIRISH:")
    
    # Har bir o'quvchi uchun ko'radigan testlarni tekshirish
    students = Student.query.all()
    
    for student in students:
        user = User.query.get(student.user_id)
        group = Group.query.get(student.group_id)
        
        print(f"\n👤 O'QUVCHI: {user.full_name} ({user.username})")
        print(f"   Guruh: {group.name if group else 'Noma\'lum'}")
        
        # Bu o'quvchi ko'ra oladigan testlar
        available_tests = Test.query.filter_by(group_id=student.group_id).all()
        print(f"   Ko'ra oladigan testlar: {len(available_tests)} ta")
        
        for test in available_tests:
            print(f"     - {test.title}")
            
            # Test vaqtini tekshirish
            from datetime import datetime
            now = datetime.utcnow()
            
            if now < test.start_time:
                print(f"       ⏰ Hali boshlanmadi ({test.start_time})")
            elif now > test.end_time:
                print(f"       ⏰ Tugagan ({test.end_time})")
            else:
                print(f"       ✅ Faol (hozir topshirish mumkin)")
        
        if not available_tests:
            print(f"   ❌ Bu guruhga test qo'yilmagan")
