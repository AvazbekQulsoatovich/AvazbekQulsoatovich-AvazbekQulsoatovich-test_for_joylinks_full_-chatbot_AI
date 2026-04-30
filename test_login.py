from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin found: {admin.username}")
        print(f"Password hash: {admin.password_hash[:50]}...")
        
        # Test password verification
        test_password = 'admin123'
        if check_password_hash(admin.password_hash, test_password):
            print("Password verification: SUCCESS")
        else:
            print("Password verification: FAILED")
            
        # Test wrong password
        wrong_password = 'wrong'
        if check_password_hash(admin.password_hash, wrong_password):
            print("Wrong password test: FAILED (should not pass)")
        else:
            print("Wrong password test: SUCCESS (correctly rejected)")
    else:
        print("Admin user not found!")
