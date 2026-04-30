from app import app, db, TestResult, Student, User, Test

with app.app_context():
    print("=== TEST NATIJALARI TEKSHIRUVI ===")
    print()
    
    # Barcha test natijalarini ko'rish
    results = TestResult.query.all()
    
    print(f"Jami test natijalari: {len(results)}")
    print()
    
    for result in results:
        student = Student.query.get(result.student_id)
        user = User.query.get(student.user_id) if student else None
        test = Test.query.get(result.test_id)
        
        print(f"📊 NATIJA:")
        print(f"   O'quvchi: {user.full_name if user else 'Noma\'lum'} ({user.username if user else 'Noma\'lum'})")
        print(f"   Test: {test.title if test else 'Noma\'lum'}")
        print(f"   Ball: {result.score}/{result.total_questions}")
        print(f"   Foiz: {result.percentage}%")
        print(f"   Vaqt: {result.submitted_at}")
        print()
    
    # Asilbekning test natijasini tekshirish
    asilbek_user = User.query.filter_by(username='assi').first()
    if asilbek_user:
        asilbek_student = Student.query.filter_by(user_id=asilbek_user.id).first()
        
        # Asilbekning yanvar test natijasi
        yanvar_test = Test.query.filter_by(title='yanvar test').first()
        
        existing_result = TestResult.query.filter_by(student_id=asilbek_student.id, test_id=yanvar_test.id).first()
        
        if existing_result:
            print("❌ Asilbek yanvar testini allaqachon topshirgan!")
            print(f"   Ball: {existing_result.score}/{existing_result.total_questions}")
            print(f"   Vaqt: {existing_result.submitted_at}")
        else:
            print("✅ Asilbek yanvar testini hali topshirmagan")
    
    # Test natijalarini tozalash (agar kerak bo'lsa)
    print("\n=== TEST NATIJALARINI TOZALASH ===")
    
    # Asilbekning test natijasini o'chirish
    if asilbek_user and yanvar_test and existing_result:
        db.session.delete(existing_result)
        db.session.commit()
        print("✅ Asilbekning test natijasi o'chirildi")
        print("Endi qayta topshirishi mumkin!")
