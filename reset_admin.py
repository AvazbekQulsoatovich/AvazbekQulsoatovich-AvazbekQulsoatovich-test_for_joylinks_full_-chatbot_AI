from app import app, db, User
from werkzeug.security import generate_password_hash
import sys

def reset_password(username, new_password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        hashed_pw = generate_password_hash(new_password)
        
        if user:
            print(f"User {username} found. Resetting password...")
            user.password_hash = hashed_pw
            db.session.commit()
            print("Password reset successfully.")
        else:
            print(f"User {username} not found. Creating new admin...")
            u = User(username=username, role='admin', full_name='Main Admin', password_hash=hashed_pw)
            db.session.add(u)
            db.session.commit()
            print("Admin created successfully.")

if __name__ == "__main__":
    reset_password('admin', 'admin123')
