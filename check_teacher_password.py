from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    print("=== TEACHER PASSWORD CHECK ===")
    
    # Avazbek userni topish
    avazbek_user = User.query.filter_by(username='avazbek').first()
    
    if avazbek_user:
        print(f"✅ Avazbek user topildi:")
        print(f"   ID: {avazbek_user.id}")
        print(f"   Username: {avazbek_user.username}")
        print(f"   Full Name: {avazbek_user.full_name}")
        print(f"   Role: {avazbek_user.role}")
        
        # Parolni tekshirish
        passwords_to_try = ['avazbek123', 'avazbek', 'password', '123456']
        
        working_password = None
        for password in passwords_to_try:
            if check_password_hash(avazbek_user.password_hash, password):
                working_password = password
                print(f"   ✅ Parol topildi: {password}")
                break
        
        if not working_password:
            print(f"   ❌ Hech qanday parol ishlamadi")
            print(f"   🔍 Hash: {avazbek_user.password_hash[:50]}...")
            
            # Avazbek uchun yangi parol o'rnatish
            from werkzeug.security import generate_password_hash
            new_password = 'avazbek123'
            avazbek_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"   🔧 Yangi parol o'rnatildi: {new_password}")
    else:
        print(f"❌ Avazbek user topilmadi!")
