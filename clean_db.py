import os
from app import app, db, Branch, User, Teacher, Student, Group, Course, Test, Question, TestResult
from werkzeug.security import generate_password_hash

def reset_database():
    print("🗑️ TOZALASH BOSHLANDI (Database Reset)...")
    
    with app.app_context():
        # 1. Barcha jadvallarni o'chirish
        db.drop_all()
        print("✅ Barcha jadvallar o'chirildi.")
        
        # 2. Yangidan yaratish
        db.create_all()
        print("✅ Barcha jadvallar qayta yaratildi.")
        
        # 3. Super Admin yaratish
        super_admin = User(
            username='Avazbek',
            password_hash=generate_password_hash('jumanazarov'),
            role='superadmin',
            full_name='Avazbek Jumanazarov',
            branch_id=None
        )
        db.session.add(super_admin)
        db.session.commit()
        print("👑 Super Admin yaratildi: Avazbek / jumanazarov")
        
    print("\n🚀 Tizim toza va deployga tayyor!")

if __name__ == '__main__':
    reset_database()
