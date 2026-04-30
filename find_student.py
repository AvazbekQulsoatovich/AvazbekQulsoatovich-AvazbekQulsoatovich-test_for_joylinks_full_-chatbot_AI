#!/usr/bin/env python3
from app import app, db, User, Student

def find_student():
    with app.app_context():
        # Find user with username student54
        user = User.query.filter_by(username='student54').first()
        
        if user:
            print("=" * 60)
            print("STUDENT54 MA'LUMOTLARI")
            print("=" * 60)
            print(f"Login: {user.username}")
            print(f"To'liq ism: {user.full_name}")
            print(f"Rol: {user.role}")
            print("")
            print("⚠️ ESLATMA: Parol hash shaklida saqlanadi.")
            print("Agar parolni bilmasangiz, yangi parol o'rnatishingiz kerak.")
            print("")
            
            # Check if has student profile
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                print(f"Guruh: {student.group.name}")
                print(f"Guruh ID: {student.group_id}")
            
            print("=" * 60)
            print("")
            print("💡 PAROLNI TIKLASH UCHUN:")
            print("   Admin panelda Students → Edit → Yangi parol kiriting")
            print("")
        else:
            print("❌ student54 topilmadi!")
            print("")
            print("Mavjud studentlar:")
            students = User.query.filter_by(role='student').limit(10).all()
            for s in students:
                print(f"  - {s.username} ({s.full_name})")

if __name__ == "__main__":
    find_student()
