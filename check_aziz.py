from app import app, db, User, Student
from werkzeug.security import check_password_hash

with app.app_context():
    print("=== AZIZ USER TEKSHIRUVI ===")
    
    # Aziz userni topish
    aziz_user = User.query.filter_by(username='aziz').first()
    
    if aziz_user:
        print(f"✅ Aziz user topildi:")
        print(f"   ID: {aziz_user.id}")
        print(f"   Username: {aziz_user.username}")
        print(f"   Full Name: {aziz_user.full_name}")
        print(f"   Role: {aziz_user.role}")
        
        # Parolni tekshirish
        passwords_to_try = ['aziz123', 'aziz', 'password', '123456']
        
        working_password = None
        for password in passwords_to_try:
            if check_password_hash(aziz_user.password_hash, password):
                working_password = password
                print(f"   ✅ Parol topildi: {password}")
                break
        
        if not working_password:
            print(f"   ❌ Hech qanday parol ishlamadi")
            print(f"   🔍 Hash: {aziz_user.password_hash[:50]}...")
            
            # Aziz uchun yangi parol o'rnatish
            from werkzeug.security import generate_password_hash
            new_password = 'aziz123'
            aziz_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"   🔧 Yangi parol o'rnatildi: {new_password}")
    else:
        print(f"❌ Aziz user topilmadi!")
        
        # Aziz student profilini tekshirish
        aziz_student = Student.query.filter_by(user_id=User.query.filter_by(username='aziz').first().id).first() if User.query.filter_by(username='aziz').first() else None
        if aziz_student:
            print(f"   📚 Aziz student profili bor")
        else:
            print(f"   ❌ Aziz student profili yo'q")
