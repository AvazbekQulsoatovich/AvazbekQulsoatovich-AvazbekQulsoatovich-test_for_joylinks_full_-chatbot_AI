from app import app, db, User, Student, Group, Teacher
from werkzeug.security import check_password_hash

with app.app_context():
    print("=== O'QUVCHI LOGIN TASHKISHI ===")
    print()
    
    # Barcha o'quvchilarni tekshirish
    students = Student.query.all()
    
    for i, student in enumerate(students, 1):
        user = User.query.get(student.user_id)
        group = Group.query.get(student.group_id)
        teacher = Teacher.query.get(group.teacher_id) if group else None
        teacher_user = User.query.get(teacher.user_id) if teacher else None
        
        print(f"{i}. O'QUVCHI: {user.full_name}")
        print(f"   Username: {user.username}")
        print(f"   Yaratuvchi: {teacher_user.full_name if teacher_user else 'Noma\'lum'}")
        print(f"   Guruh: {group.name if group else 'Noma\'lum'}")
        
        # Parolni tekshirish
        possible_passwords = [
            user.username,  # username
            user.username + '123',  # username + 123
            'password',  # standart parol
            '123456',  # oddiy parol
        ]
        
        working_password = None
        for password in possible_passwords:
            if check_password_hash(user.password_hash, password):
                working_password = password
                break
        
        if working_password:
            print(f"   ✅ Ishlaydigan parol: {working_password}")
        else:
            print(f"   ❌ Parol noma'lum!")
            print(f"   🔍 Hash: {user.password_hash[:50]}...")
        
        print()
    
    print("=== LOGIN TESTLARI ===")
    
    # Har bir o'quvchi uchun login testi
    for student in students:
        user = User.query.get(student.user_id)
        
        # Username + 123 patternini tekshirish
        test_password = user.username + '123'
        
        print(f"Testing {user.username} / {test_password}:")
        if check_password_hash(user.password_hash, test_password):
            print(f"   ✅ Parol to'g'ri!")
        else:
            print(f"   ❌ Parol noto'g'ri!")
            
            # Boshqa variantlarni tekshirish
            for alt_password in possible_passwords:
                if check_password_hash(user.password_hash, alt_password):
                    print(f"   ✅ Alternativ parol topildi: {alt_password}")
                    break
        print()
