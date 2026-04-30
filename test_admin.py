from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin user exists: {admin.username}")
    else:
        # Create admin user
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name='System Administrator'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
    
    # List all users
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"Username: {user.username}, Role: {user.role}")
