from app import app, db, User, Teacher

with app.app_context():
    print("Checking users in database:")
    
    # Check all users
    users = User.query.all()
    for user in users:
        print(f"User: {user.username}, Role: {user.role}, ID: {user.id}")
    
    # Check teacher profiles
    teachers = Teacher.query.all()
    for teacher in teachers:
        print(f"Teacher Profile - User ID: {teacher.user_id}, Course ID: {teacher.course_id}")
    
    # Check if teacher1 exists and has profile
    teacher_user = User.query.filter_by(username='teacher1').first()
    if teacher_user:
        teacher_profile = Teacher.query.filter_by(user_id=teacher_user.id).first()
        if teacher_profile:
            print(f"✅ Teacher1 profile found: User ID {teacher_profile.user_id}, Course ID {teacher_profile.course_id}")
        else:
            print(f"❌ Teacher1 profile NOT found")
    else:
        print(f"❌ Teacher1 user NOT found")
