import logging
import os
from flask import Flask
from app import db, User, Branch  # Adjust based on your imports
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database for production."""
    logger.info("🚀 Initializing production database...")
    
    # In some environments, like Heroku or Kubernetes, 
    # we might want to ensure the database exists first.
    # SQLALchemy create_all handles this for SQLite, but for Postgres 
    # the database itself must already exist.
    
    try:
        db.create_all()
        logger.info("✅ Database tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

    # Check for default superadmin
    try:
        username = os.environ.get('DEFAULT_ADMIN_USER', 'admin')
        password = os.environ.get('DEFAULT_ADMIN_PASS', 'secure_admin_password_2024')
        
        admin = User.query.filter_by(username=username).first()
        if not admin:
            logger.info(f"👤 Creating default superadmin: {username}")
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='superadmin',
                full_name='System Administrator'
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info("✅ Default superadmin created.")
        else:
            logger.info("ℹ️ Superadmin already exists.")
            
    except Exception as e:
        logger.error(f"❌ Error seeding initial data: {e}")
        return False
        
    logger.info("🎉 Database initialization complete.")
    return True

if __name__ == '__main__':
    from app import app
    with app.app_context():
        init_db()
