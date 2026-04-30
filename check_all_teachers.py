from app import app, db, User, Teacher

with app.app_context():
    print("=== BARCHA TEACHERLAR ===")
    
    # Barcha teacher userlarni ko'rish
    teacher_users = User.query.filter_by(role='teacher').all()
    
    print(f"Jami teacher userlar: {len(teacher_users)}")
    
    for user in teacher_users:
        print(f"\n👤 TEACHER:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        
        # Teacher profilini tekshirish
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if teacher:
            print(f"   Teacher ID: {teacher.id}")
            print(f"   Course ID: {teacher.course_id}")
        else:
            print(f"   ❌ Teacher profili yo'q")
    
    # Barcha teacher profilarni ko'rish
    print(f"\n=== TEACHER PROFILES ===")
    teachers = Teacher.query.all()
    
    print(f"Jami teacher profillar: {len(teachers)}")
    
    for teacher in teachers:
        user = User.query.get(teacher.user_id)
        print(f"\n📚 TEACHER PROFILE:")
        print(f"   ID: {teacher.id}")
        print(f"   User: {user.full_name if user else 'Noma\'lum'} ({user.username if user else 'Noma\'lum'})")
        print(f"   Course ID: {teacher.course_id}")
    
    # Login test qilish uchun birinchi teacherni tanlash
    if teacher_users:
        first_teacher = teacher_users[0]
        print(f"\n🔑 LOGIN TEST UCHUN:")
        print(f"   Username: {first_teacher.username}")
        print(f"   Password: {first_teacher.username}123 (standart)")
