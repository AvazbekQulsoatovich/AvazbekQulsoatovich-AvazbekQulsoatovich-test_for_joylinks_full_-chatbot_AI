from app import app, db, User, Teacher, Student, Group
from werkzeug.security import check_password_hash

def check_users():
    with app.app_context():
        print("--- User List ---")
        users = User.query.all()
        for user in users:
            profile_exists = False
            if user.role == 'student':
                profile_exists = Student.query.filter_by(user_id=user.id).first() is not None
            elif user.role == 'teacher':
                profile_exists = Teacher.query.filter_by(user_id=user.id).first() is not None
            elif user.role == 'admin':
                profile_exists = True # Admins don't have separate profiles in this system usually
            
            print(f"ID: {user.id} | Username: {user.username} | Role: {user.role} | Name: {user.full_name} | Profile: {'✅' if profile_exists else '❌ MISSING'}")
            
        print("\n--- Testing Specific Credentials (if known) ---")
        # Common default credentials mentioned in previous summaries
        test_creds = [
            ('Avazbek', 'jumanazarov'),
            ('admin', 'admin123')
        ]
        
        for username, password in test_creds:
            user = User.query.filter_by(username=username).first()
            if user:
                match = check_password_hash(user.password_hash, password)
                print(f"Testing {username}:{password} -> {'✅ MATCH' if match else '❌ FAIL'}")
                
                # Test case-insensitivity
                lowercase_user = User.query.filter_by(username=username.lower()).first()
                if lowercase_user and lowercase_user.id == user.id:
                    print(f"Case-insensitive match for {username.lower()} -> ✅ YES")
                else:
                    print(f"Case-insensitive match for {username.lower()} -> ❌ NO")
            else:
                print(f"Testing {username}:{password} -> ❌ USER NOT FOUND")

if __name__ == "__main__":
    check_users()
