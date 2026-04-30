from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    print("=== WEBDEVAJ PASSWORD CHECK ===")
    
    # webdevaj userni topish
    webdevaj_user = User.query.filter_by(username='webdevaj').first()
    
    if webdevaj_user:
        print(f"✅ webdevaj user topildi:")
        print(f"   ID: {webdevaj_user.id}")
        print(f"   Username: {webdevaj_user.username}")
        print(f"   Full Name: {webdevaj_user.full_name}")
        print(f"   Role: {webdevaj_user.role}")
        
        # Parolni tekshirish
        passwords_to_try = ['webdevaj123', 'webdevaj', 'password', '123456', 'avazbek123']
        
        working_password = None
        for password in passwords_to_try:
            if check_password_hash(webdevaj_user.password_hash, password):
                working_password = password
                print(f"   ✅ Parol topildi: {password}")
                break
        
        if not working_password:
            print(f"   ❌ Hech qanday parol ishlamadi")
            print(f"   🔍 Hash: {webdevaj_user.password_hash[:50]}...")
            
            # webdevaj uchun yangi parol o'rnatish
            from werkzeug.security import generate_password_hash
            new_password = 'webdevaj123'
            webdevaj_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"   🔧 Yangi parol o'rnatildi: {new_password}")
    else:
        print(f"❌ webdevaj user topilmadi!")
