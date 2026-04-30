from app import app, db, Test
from datetime import datetime

with app.app_context():
    print("=== TEST VAQTLARI TEKSHIRUVI ===")
    print()
    
    # Hozirgi vaqt
    now = datetime.utcnow()
    print(f"Hozirgi vaqt (UTC): {now}")
    print(f"Hozirgi vaqt (O'zbekiston): {now.replace(hour=now.hour+5)}")  # +5 UTC for Uzbekistan
    print()
    
    # Barcha testlarni tekshirish
    tests = Test.query.all()
    
    for test in tests:
        print(f"📝 TEST: {test.title}")
        print(f"   Boshlanish: {test.start_time}")
        print(f"   Tugash: {test.end_time}")
        print(f"   Davomiyligi: {test.duration_minutes} daqiqa")
        
        # Vaqtni solishtirish
        if now < test.start_time:
            time_until_start = test.start_time - now
            print(f"   ⏰ Holi boshlanmadi! {time_until_start} dan keyin boshlanadi")
        elif now > test.end_time:
            print(f"   ⏰ Tugagan! {now - test.end_time} oldin tugagan")
        else:
            print(f"   ✅ FAOL! Endi topshirish mumkin")
        
        print()
    
    # Faol test yaratish (agar kerak bo'lsa)
    print("=== FAOL TEST YARATISH ===")
    
    # Afruz uchun faol test yaratish
    from app import Group, Teacher
    
    # Afruz guruhini topish
    afruz_student = db.session.query(Test).join(Group).filter(Group.name == 'ing-tili14:00-16:00').first()
    
    if afruz_student:
        print(f"Afruz guruhida test bor: {afruz_student.title}")
        
        # Test vaqtini hozirgi vaqtdan boshlab 1 soat keyin tugashiga o'zgartirish
        afruz_student.start_time = now.replace(second=0, microsecond=0)
        afruz_student.end_time = now.replace(hour=now.hour+1, second=0, microsecond=0)
        db.session.commit()
        
        print(f"✅ Test vaqti o'zgartirildi:")
        print(f"   Yangi boshlanish: {afruz_student.start_time}")
        print(f"   Yangi tugash: {afruz_student.end_time}")
    else:
        print("❌ Afruz guruhida test topilmadi")
