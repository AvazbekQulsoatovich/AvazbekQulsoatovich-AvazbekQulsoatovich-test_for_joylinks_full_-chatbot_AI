from app import app, db, Test
from datetime import datetime

with app.app_context():
    print("=== AZIZ TESTINI FAOL QILISH ===")
    
    # Aziz testini topish (yanvar test)
    test = Test.query.filter_by(title='yanvar').first()
    
    if test:
        print(f"Test topildi: {test.title}")
        print(f"Eski vaqt: {test.start_time} - {test.end_time}")
        
        # Vaqtni hozirgi vaqtdan boshlab 1 soat keyin tugashiga o'zgartirish
        now = datetime.utcnow()
        test.start_time = now.replace(second=0, microsecond=0)
        test.end_time = now.replace(hour=now.hour+1, second=0, microsecond=0)
        
        db.session.commit()
        
        print(f"✅ Yangi vaqt: {test.start_time} - {test.end_time}")
        print("✅ Test faol qilindi!")
    else:
        print("❌ Test topilmadi")
