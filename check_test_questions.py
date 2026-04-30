from app import app, db, Test, Question

with app.app_context():
    print("=== TEST SAVOLLARI TEKSHIRUVI ===")
    print()
    
    # Barcha testlarni tekshirish
    tests = Test.query.all()
    
    for test in tests:
        print(f"📝 TEST: {test.title}")
        print(f"   Test ID: {test.id}")
        
        # Test savollarini tekshirish
        questions = Question.query.filter_by(test_id=test.id).all()
        print(f"   Savollar soni: {len(questions)}")
        
        for i, question in enumerate(questions, 1):
            print(f"     {i}. {question.question_text}")
            print(f"        A) {question.option_a}")
            print(f"        B) {question.option_b}")
            print(f"        C) {question.option_c}")
            print(f"        D) {question.option_d}")
            print(f"        ✅ To'g'ri javob: {question.correct_answer}")
            print()
        
        if not questions:
            print(f"   ❌ Bu testda savollar yo'q!")
            
            # Test uchun namuna savol yaratish
            print(f"   🔧 Namuna savol qo'shilmoqda...")
            sample_question = Question(
                test_id=test.id,
                question_text="Bu test uchun namuna savol?",
                option_a="Javob A",
                option_b="Javob B", 
                option_c="Javob C",
                option_d="Javob D",
                correct_answer="A"
            )
            db.session.add(sample_question)
            db.session.commit()
            print(f"   ✅ Namuna savol qo'shildi!")
        
        print("-" * 50)
