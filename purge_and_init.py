from app import app, db, User, Teacher, Student, Group, Test, Question, TestResult, Course
from werkzeug.security import generate_password_hash

def purge_and_init():
    with app.app_context():
        print("Purging database...")
        # Delete in order of dependencies
        TestResult.query.delete()
        Question.query.delete()
        Test.query.delete()
        Student.query.delete()
        Group.query.delete()
        Teacher.query.delete()
        Course.query.delete()
        User.query.delete()
        
        db.session.commit()
        print("Database purged successfully.")
        
        print("Creating new admin account...")
        new_admin = User(
            username='Avazbek',
            password_hash=generate_password_hash('jumanazarov'),
            role='admin',
            full_name='Avazbek Jumanazarov'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("New admin created: Avazbek / jumanazarov")

if __name__ == "__main__":
    purge_and_init()
