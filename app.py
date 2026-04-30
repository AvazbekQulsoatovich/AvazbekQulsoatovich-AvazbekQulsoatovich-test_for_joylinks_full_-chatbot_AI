import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response, session, send_from_directory
from werkzeug.utils import secure_filename
import dotenv
dotenv.load_dotenv()
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
import base64
import os
import ast
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import time
import google.generativeai as genai
try:
    from groq import Groq
except ImportError:
    Groq = None

# Environment Variables
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL')

# PostgreSQL Fix: Heroku and some others use 'postgres://', but SQLAlchemy 1.4+ requires 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure logging
LOG_LEVEL = logging.INFO if IS_PRODUCTION else logging.DEBUG
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use session-based SECRET_KEY if provided, otherwise development default
app.config['SECRET_KEY'] = SECRET_KEY
# Use DATABASE_URL if provided, otherwise default SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///joylinks_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 7 * 1024 * 1024 # 7MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Blocked extensions (everything else is allowed)
BLOCKED_EXTENSIONS = {'apk', 'exe', 'bat', 'sh', 'cmd', 'msi', 'com', 'scr'}

def allowed_file(filename):
    if '.' not in filename:
        return True
    ext = filename.rsplit('.', 1)[1].lower()
    return ext not in BLOCKED_EXTENSIONS

def delete_upload_file(filename):
    """Safely deletes a file from the upload folder if it exists."""
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Deleted file: {filename}")
        except Exception as e:
            logger.error(f"❌ Error deleting file {filename}: {e}")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Session configuration
# SECURE should be True in production (requires HTTPS)
app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Timezone setup
UZB_TZ = pytz.timezone('Asia/Tashkent')

def get_now():
    """Returns current Tashkent time without timezone info for comparison with DB."""
    return datetime.now(UZB_TZ).replace(tzinfo=None)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Gemini AI Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Model priorities - use stable 1.5 Flash first for reliability
    GEMINI_MODELS = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-pro-latest']
    gemini_model = None
    for model_name in GEMINI_MODELS:
        try:
            gemini_model = genai.GenerativeModel(model_name)
            logger.info(f"✅ Gemini AI configured with model: {model_name}")
            break
        except Exception as e:
            logger.warning(f"⚠️ Model {model_name} not available: {e}")
else:
    gemini_model = None
    logger.warning("⚠️ GEMINI_API_KEY not set.")

# Groq AI Configuration (Recommended for better Free Tier performance)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
groq_client = None
if GROQ_API_KEY and Groq:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq AI (Llama 3.1) configured as primary engine.")
    except Exception as e:
        logger.error(f"❌ Error configuring Groq: {e}")

# Database Models
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='branch', lazy=True)
    courses = db.relationship('Course', backref='branch', lazy=True)
    groups = db.relationship('Group', backref='branch', lazy=True)
    tests = db.relationship('Test', backref='branch', lazy=True)
class User(UserMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint('branch_id', 'username', name='uix_branch_username'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # superadmin, admin, teacher, student
    full_name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=True, index=True)
    
    # Relationships
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
    
    # Relationships
    groups = db.relationship('Group', backref='teacher', lazy=True, cascade='all, delete-orphan')
    course = db.relationship('Course', backref='teachers', lazy=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False, index=True)
    
    # Relationships
    students = db.relationship('Student', backref='group', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='group', lazy=True, cascade='all, delete-orphan')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False, index=True)
    
    # Relationships
    results = db.relationship('TestResult', backref='student', lazy=True, cascade='all, delete-orphan')

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)  
    duration_minutes = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, default=get_now)
    end_time = db.Column(db.DateTime, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=get_now)
    
    # Practical task fields
    has_practical = db.Column(db.Boolean, default=False)
    practical_file = db.Column(db.String(255))
    practical_description = db.Column(db.Text)
    
    # Relationships
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('TestResult', backref='test', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.DateTime, default=get_now)
    answers = db.Column(db.Text)  # JSON string of student answers
    practical_submission = db.Column(db.String(255)) # Path to uploaded file
    practical_score = db.Column(db.Integer, nullable=True)  # Admin grade 0-100
    practical_feedback = db.Column(db.Text, nullable=True)  # Admin feedback

class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, default=get_now)
    is_submitted = db.Column(db.Boolean, default=False)

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('404.html'), 500

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:
            flash('Kirish taqiqlangan. Admin huquqlari kerak.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            flash('Kirish taqiqlangan. Super Admin huquqlari kerak.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Kirish taqiqlangan. O\'qituvchi huquqlari kerak.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Kirish taqiqlangan. O\'quvchi huquqlari kerak.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'superadmin':
            return redirect(url_for('superadmin_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        branch_id = request.form.get('branch_id')
        
        logger.info(f"🔍 Login attempt: username={username}, branch={branch_id}")
        
        # Superadmin bypasses branch
        user = None
        # Smart Login Logic: If branch not selected, try to find unique user globally
        if branch_id == '0':
             user = User.query.filter_by(username=username, role='superadmin').first()
        elif branch_id and branch_id != 'None':
            user = User.query.filter_by(branch_id=branch_id, username=username).first()
        else:
            # Automatic detection
            potential_users = User.query.filter_by(username=username).all()
            if len(potential_users) == 1:
                user = potential_users[0]
            elif len(potential_users) > 1:
                flash('Foydalanuvchi bir nechta filialda mavjud. Iltimos, filialni tanlang!', 'warning')
                return redirect(url_for('login'))
        
        if user:
            logger.info(f"🔍 User found: {user.full_name} ({user.role})")
            logger.info(f"🔍 Password check: {check_password_hash(user.password_hash, password)}")
        
        if user and check_password_hash(user.password_hash, password):
            logger.info(f"✅ Login successful for {user.full_name}")
            login_user(user)
            session.permanent = True
            flash(f'Xush kelibsiz, {user.full_name}! Muvaffaqiyatli kirish!', 'success')
            
            # Debug info
            logger.info(f"🔐 User logged in: {user.full_name} ({user.role})")
            logger.info(f"🔐 Current user after login: {current_user.is_authenticated if current_user else 'No current_user'}")
            logger.info(f"🔐 Session data: {dict(session)}")
            
            if user.role == 'superadmin':
                logger.info("👑 Redirecting to superadmin dashboard")
                return redirect(url_for('superadmin_dashboard'))
            elif user.role == 'admin':
                logger.info("👑 Redirecting to admin dashboard")
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'teacher':
                logger.info("👨‍🏫 Redirecting to teacher dashboard")
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                logger.info("👨‍🎓 Redirecting to student dashboard")
                return redirect(url_for('student_dashboard'))
        else:
            logger.error("❌ Invalid login attempt")
            flash('Noto\'g\'ri login, parol yoki filial', 'danger')
    
    branches = Branch.query.all()
    return render_template('login_modern.html', branches=branches)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Siz tizimdan chiqdingiz.', 'info')
    return redirect(url_for('login'))

# Super Admin Routes
@app.route('/superadmin/dashboard')
@superadmin_required
def superadmin_dashboard():
    total_branches = Branch.query.count()
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.count()
    total_tests = Test.query.count()
    total_groups = Group.query.count()
    
    branches = Branch.query.all()
    
    # Tashkent vaqtini olish (get_now helper)
    current_time = get_now()
    
    return render_template('superadmin/dashboard_modern.html', 
                         total_branches=total_branches,
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         total_tests=total_tests,
                         total_groups=total_groups,
                         branches=branches,
                         current_time=current_time)

# Admin Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.join(User).filter(User.branch_id == current_user.branch_id).count()
    total_teachers = Teacher.query.join(User).filter(User.branch_id == current_user.branch_id).count()
    total_courses = Course.query.filter_by(branch_id=current_user.branch_id).count()
    total_tests = Test.query.filter_by(branch_id=current_user.branch_id).count()
    total_groups = Group.query.filter_by(branch_id=current_user.branch_id).count()
    
    # Tashkent vaqtini olish (get_now helper)
    current_time = get_now()
    
    return render_template('admin/dashboard_modern.html', 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         total_tests=total_tests,
                         total_groups=total_groups,
                         current_time=current_time)

@app.route('/admin/courses')
@admin_required
def admin_courses():
    page = request.args.get('page', 1, type=int)
    courses_q = Course.query if current_user.role == 'superadmin' else Course.query.filter_by(branch_id=current_user.branch_id)
    pagination = courses_q.paginate(page=page, per_page=10, error_out=False)
    courses = pagination.items
    return render_template('admin/courses_modern.html', courses=courses, pagination=pagination)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@admin_required
def admin_add_course():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name or len(name) < 3 or len(name) > 100:
            flash('Kurs nomi 3 dan 100 gacha belgidan iborat bo\'lishi kerak!', 'danger')
            return redirect(url_for('admin_add_course'))
            
        course = Course(name=name, description=description, branch_id=current_user.branch_id)
        db.session.add(course)
        db.session.commit()
        
        flash('Kurs muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/add_course_modern.html')

@app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_course(course_id):
    course = Course.query.filter_by(id=course_id, branch_id=current_user.branch_id).first_or_404()
    
    if request.method == 'POST':
        course.name = request.form.get('name')
        course.description = request.form.get('description')
        
        db.session.commit()
        flash('Kurs muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/edit_course_modern.html', course=course)

@app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
@admin_required
def admin_delete_course(course_id):
    course = Course.query.filter_by(id=course_id, branch_id=current_user.branch_id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    flash('Kurs muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/groups/add', methods=['GET', 'POST'])
@admin_required
def admin_add_group():
    if request.method == 'POST':
        name = request.form.get('name')
        teacher_id = request.form.get('teacher_id')
        
        if not name or len(name) < 2 or len(name) > 50:
            flash('Guruh nomi 2 dan 50 gacha belgidan iborat bo\'lishi kerak!', 'danger')
            return redirect(url_for('admin_add_group'))
            
        group = Group(name=name, teacher_id=teacher_id, branch_id=current_user.branch_id)
        db.session.add(group)
        db.session.commit()
        
        flash('Guruh muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_groups'))
    
    teachers_q = db.session.query(Teacher, User, Course).join(User).join(Course)
    if current_user.role != 'superadmin':
        teachers_q = teachers_q.filter(User.branch_id == current_user.branch_id)
    teachers = teachers_q.all()
    return render_template('admin/add_group_modern.html', teachers=teachers)

@app.route('/admin/groups/edit/<int:group_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_group(group_id):
    group = Group.query.filter_by(id=group_id, branch_id=current_user.branch_id).first_or_404()
    
    if request.method == 'POST':
        group.name = request.form.get('name')
        group.teacher_id = request.form.get('teacher_id')
        db.session.commit()
        flash('Guruh muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_groups'))
    
    teachers_q = db.session.query(Teacher, User, Course).join(User).join(Course)
    if current_user.role != 'superadmin':
        teachers_q = teachers_q.filter(User.branch_id == current_user.branch_id)
    teachers = teachers_q.all()
    return render_template('admin/edit_group_modern.html', group=group, teachers=teachers)

@app.route('/admin/groups/delete/<int:group_id>', methods=['POST'])
@admin_required
def admin_delete_group(group_id):
    group = Group.query.filter_by(id=group_id, branch_id=current_user.branch_id).first_or_404()
    
    # 1. Cleanup all students and their files in this group
    students = Student.query.filter_by(group_id=group.id).all()
    for s in students:
        results = TestResult.query.filter_by(student_id=s.id).all()
        for res in results:
            delete_upload_file(res.practical_submission)
        # Delete user account
        if s.user:
            db.session.delete(s.user)
    
    # 2. Cleanup all tests and their files in this group
    tests = Test.query.filter_by(group_id=group.id).all()
    for t in tests:
        delete_upload_file(t.practical_file)
        
    db.session.delete(group)
    db.session.commit()
    flash('Guruh, uning o\'quvchilari va barcha fayllari muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/groups')
@admin_required
def admin_groups():
    page = request.args.get('page', 1, type=int)
    groups_q = db.session.query(Group, Teacher, User, Course).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).join(Course, Teacher.course_id == Course.id)
    if current_user.role != 'superadmin':
        groups_q = groups_q.filter(Group.branch_id == current_user.branch_id)
    pagination = groups_q.paginate(page=page, per_page=10, error_out=False)
    groups = pagination.items
    return render_template('admin/groups_modern.html', groups=groups, pagination=pagination)

@app.route('/admin/tests/add', methods=['GET', 'POST'])
@admin_required
def admin_add_test():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        group_id = request.form.get('group_id')
        start_raw = request.form.get('start_time')
        end_raw = request.form.get('end_time')
        duration_raw = request.form.get('duration_minutes')
        
        if not all([title, group_id, start_raw, end_raw, duration_raw]):
            flash('Barcha majburiy maydonlarni to\'ldiring!', 'danger')
            return redirect(url_for('admin_add_test'))

        try:
            start_time = datetime.strptime(start_raw, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_raw, '%Y-%m-%dT%H:%M')
            duration_minutes = int(duration_raw)
            
            if end_time <= start_time:
                flash('Tugash vaqti boshlanish vaqtidan keyin bo\'lishi shart!', 'danger')
                return redirect(url_for('admin_add_test'))
            
            if duration_minutes <= 0:
                flash('Davomiylik kamida 1 daqiqa bo\'lishi kerak!', 'danger')
                return redirect(url_for('admin_add_test'))
                
        except (ValueError, TypeError):
            flash('Noto\'g\'ri ma\'lumot kiritildi. Formani tekshiring.', 'danger')
            return redirect(url_for('admin_add_test'))
            
        # Handle practical task
        has_practical = request.form.get('has_practical') == 'on'
        practical_description = request.form.get('practical_description')
        practical_file_path = None
        
        if has_practical and 'practical_file' in request.files:
            file = request.files['practical_file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"task_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                practical_file_path = filename

        test = Test(
            title=title, 
            group_id=group_id, 
            start_time=start_time, 
            end_time=end_time, 
            duration_minutes=duration_minutes, 
            branch_id=current_user.branch_id,
            has_practical=has_practical,
            practical_file=practical_file_path,
            practical_description=practical_description
        )
        db.session.add(test)
        db.session.flush()
        
        # Add questions
        question_count = int(request.form.get('question_count'))
        for i in range(1, question_count + 1):
            question = Question(
                test_id=test.id,
                question_text=request.form.get(f'question_{i}_text'),
                option_a=request.form.get(f'question_{i}_a'),
                option_b=request.form.get(f'question_{i}_b'),
                option_c=request.form.get(f'question_{i}_c'),
                option_d=request.form.get(f'question_{i}_d'),
                correct_answer=request.form.get(f'question_{i}_correct')
            )
            db.session.add(question)
        
        db.session.commit()
        flash('Test muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_tests'))
    
    groups = db.session.query(Group, Teacher, User).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()
    return render_template('admin/add_test_modern.html', groups=groups)

@app.route('/admin/tests')
@admin_required
def admin_tests():
    page = request.args.get('page', 1, type=int)
    tests_q = db.session.query(Test, Group, Teacher, User).join(Group, Test.group_id == Group.id).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id)
    if current_user.role != 'superadmin':
        tests_q = tests_q.filter(Group.branch_id == current_user.branch_id)
    pagination = tests_q.paginate(page=page, per_page=10, error_out=False)
    tests = pagination.items
    current_time = get_now()
    return render_template('admin/tests_modern.html', tests=tests, current_time=current_time, pagination=pagination)

@app.route('/admin/tests/toggle/<int:test_id>', methods=['POST'])
@admin_required
def admin_toggle_test(test_id):
    test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
    test.is_active = not test.is_active
    db.session.commit()
    status = "faollashtirildi" if test.is_active else "faolsizlantirildi"
    flash(f'Test muvaffaqiyatli {status}!', 'success')
    return redirect(url_for('admin_tests'))

@app.route('/admin/tests/edit/<int:test_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_test(test_id):
    test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
    if request.method == 'POST':
        test.title = request.form.get('title')
        test.group_id = request.form.get('group_id')
        test.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        test.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        test.duration_minutes = int(request.form.get('duration_minutes'))
        
        # Update practical task
        test.has_practical = request.form.get('has_practical') == 'on'
        test.practical_description = request.form.get('practical_description')
        
        if test.has_practical and 'practical_file' in request.files:
            file = request.files['practical_file']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old file if exists
                if test.practical_file:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], test.practical_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(f"task_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                test.practical_file = filename
        
        # Update existing questions
        questions = Question.query.filter_by(test_id=test.id).all()
        for q in questions:
            q.question_text = request.form.get(f'question_{q.id}_text')
            q.option_a = request.form.get(f'question_{q.id}_a')
            q.option_b = request.form.get(f'question_{q.id}_b')
            q.option_c = request.form.get(f'question_{q.id}_c')
            q.option_d = request.form.get(f'question_{q.id}_d')
            q.correct_answer = request.form.get(f'question_{q.id}_correct')
        
        # Add new questions if any
        new_q_count = int(request.form.get('new_question_count', 0))
        for i in range(1, new_q_count + 1):
            q_text = request.form.get(f'new_question_{i}_text')
            if q_text:
                new_q = Question(
                    test_id=test.id,
                    question_text=q_text,
                    option_a=request.form.get(f'new_question_{i}_a'),
                    option_b=request.form.get(f'new_question_{i}_b'),
                    option_c=request.form.get(f'new_question_{i}_c'),
                    option_d=request.form.get(f'new_question_{i}_d'),
                    correct_answer=request.form.get(f'new_question_{i}_correct')
                )
                db.session.add(new_q)
        
        db.session.commit()
        flash('Test muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_tests'))
    
    groups = db.session.query(Group, Teacher, User).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()
    questions = Question.query.filter_by(test_id=test.id).all()
    return render_template('admin/edit_test_modern.html', test=test, groups=groups, questions=questions)

@app.route('/admin/tests/delete/<int:test_id>', methods=['POST'])
@admin_required
def admin_delete_test(test_id):
    test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
    
    # 1. Delete test's practical task file
    delete_upload_file(test.practical_file)
    
    # 2. Delete all student submissions for this test
    results = TestResult.query.filter_by(test_id=test_id).all()
    for res in results:
        delete_upload_file(res.practical_submission)
    
    db.session.delete(test)
    db.session.commit()
    flash('Test va unga tegishli barcha fayllar muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('admin_tests'))

@app.route('/admin/students/add', methods=['GET', 'POST'])
@admin_required
def admin_add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        group_id = request.form.get('group_id')
        
        # Check if username already exists
        if User.query.filter_by(username=username, branch_id=current_user.branch_id).first():
            flash('Ushbu username mavjud!', 'danger')
            return redirect(url_for('admin_add_student'))
        
        # Create user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='student',
            full_name=full_name,
            branch_id=current_user.branch_id
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create student profile
        student = Student(user_id=user.id, group_id=group_id)
        db.session.add(student)
        db.session.commit()
        
        flash('O\'quvchi muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_students'))
    
    groups = db.session.query(Group, Teacher, User).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()
    return render_template('admin/add_student_modern.html', groups=groups)

@app.route('/admin/students/edit/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_student(student_id):
    from sqlalchemy.orm import aliased
    
    student_user = aliased(User, name='student_user')
    teacher_user = aliased(User, name='teacher_user')
    
    student = db.session.query(Student, student_user, Group, Teacher, teacher_user)\
        .join(student_user, Student.user_id == student_user.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Teacher, Group.teacher_id == Teacher.id)\
        .join(teacher_user, Teacher.user_id == teacher_user.id)\
        .filter(Student.id == student_id)\
        .first_or_404()
    
    student_obj, user_obj, group_obj, teacher_obj, teacher_user_obj = student
    
    if request.method == 'POST':
        user_obj.full_name = request.form.get('full_name')
        user_obj.username = request.form.get('username')
        student_obj.group_id = request.form.get('group_id')
        
        password = request.form.get('password')
        if password:  # Only update password if provided
            user_obj.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('O\'quvchi ma\'lumotlari muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_students'))
    
    groups = db.session.query(Group, Teacher, User).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()
    return render_template('admin/edit_student_modern.html', student=student_obj, user=user_obj, groups=groups)

@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    # Get student and verify branch isolation
    student = Student.query.join(User).filter(User.branch_id == current_user.branch_id, Student.id == student_id).first_or_404()
    
    # 1. Cleanup student's practical submission files
    results = TestResult.query.filter_by(student_id=student_id).all()
    for res in results:
        delete_upload_file(res.practical_submission)
        
    # Save user reference before deleting profile
    user = student.user
    
    # Delete profile first
    db.session.delete(student)
    
    # Delete base user account if exists
    if user:
        db.session.delete(user)
        
    db.session.commit()
    flash('O\'quvchi va uning barcha fayllari muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/teachers')
@admin_required
def admin_teachers():
    page = request.args.get('page', 1, type=int)
    teachers_q = db.session.query(Teacher, User, Course).join(User).join(Course)
    if current_user.role != 'superadmin':
        teachers_q = teachers_q.filter(User.branch_id == current_user.branch_id)
    pagination = teachers_q.paginate(page=page, per_page=10, error_out=False)
    teachers = pagination.items
    return render_template('admin/teachers_modern.html', teachers=teachers, pagination=pagination)

@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@admin_required
def admin_add_teacher():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        course_id = request.form.get('course_id')
        
        # Check if username already exists
        if User.query.filter_by(username=username, branch_id=current_user.branch_id).first():
            flash('Ushbu login allaqachon mavjud!', 'danger')
            return redirect(url_for('admin_add_teacher'))
        
        # Create user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='teacher',
            full_name=full_name,
            branch_id=current_user.branch_id
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create teacher profile
        teacher = Teacher(user_id=user.id, course_id=course_id)
        db.session.add(teacher)
        db.session.commit()
        
        flash("O'qituvchi muvaffaqiyatli qo'shildi!", 'success')
        return redirect(url_for('admin_teachers'))
    
    courses = Course.query.all() if current_user.role == 'superadmin' else Course.query.filter_by(branch_id=current_user.branch_id).all()
    return render_template('admin/add_teacher_modern.html', courses=courses)

@app.route('/admin/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_teacher(teacher_id):
    teacher = Teacher.query.join(User).filter(User.branch_id == current_user.branch_id, Teacher.id == teacher_id).first_or_404()
    
    if request.method == 'POST':
        teacher.user.full_name = request.form.get('full_name')
        teacher.course_id = request.form.get('course_id')
        
        password = request.form.get('password')
        if password:  # Only update password if provided
            teacher.user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash("O'qituvchi ma'lumotlari muvaffaqiyatli yangilandi!", 'success')
        return redirect(url_for('admin_teachers'))
    
    courses = Course.query.all() if current_user.role == 'superadmin' else Course.query.filter_by(branch_id=current_user.branch_id).all()
    return render_template('admin/edit_teacher_modern.html', teacher=teacher, courses=courses)

@app.route('/admin/teachers/delete/<int:teacher_id>', methods=['POST'])
@admin_required
def admin_delete_teacher(teacher_id):
    # Verify teacher belongs to admin's branch
    teacher = Teacher.query.join(User).filter(User.branch_id == current_user.branch_id, Teacher.id == teacher_id).first_or_404()
    # Save reference for cleanup
    user = teacher.user
    
    # The teacher profile deletion will handle groups if cascade is set, 
    # but we manually clean up to be absolutely safe as requested
    groups = Group.query.filter_by(teacher_id=teacher.id).all()
    for g in groups:
        # Students in these groups should ideally be reassigned or deleted.
        # Here we follow "aggressive delete" to ensure perfection of choice.
        students = Student.query.filter_by(group_id=g.id).all()
        for s in students:
            # Delete student along with their user for full cleanup
            s_user = s.user
            db.session.delete(s)
            if s_user:
                db.session.delete(s_user)
        db.session.delete(g)

    # Delete teacher profile itself
    db.session.delete(teacher)
    
    # Finally delete the base teacher user account
    if user:
        db.session.delete(user)
        
    db.session.commit()
    flash("O'qituvchi va unga bog'liq barcha ma'lumotlar o'chirildi!", 'success')
    return redirect(url_for('admin_teachers'))

@app.route('/admin/teachers/view/<int:teacher_id>')
@admin_required
def admin_view_teacher(teacher_id):
    teacher_q = db.session.query(Teacher, User, Course).join(User).join(Course).filter(Teacher.id == teacher_id)
    if current_user.role != 'superadmin':
        teacher_q = teacher_q.filter(User.branch_id == current_user.branch_id)
    teacher = teacher_q.first_or_404()
    teacher_obj, user_obj, course_obj = teacher
    
    # Get teacher's groups and students
    groups = Group.query.filter_by(teacher_id=teacher_id).all()
    students = db.session.query(Student, User, Group).join(User).join(Group).filter(Group.teacher_id == teacher_id).all()
    
    return render_template('admin/view_teacher_modern.html', teacher=teacher_obj, user=user_obj, course=course_obj, groups=groups, students=students)

@app.route('/admin/students')
@admin_required
def admin_students():
    from sqlalchemy.orm import aliased
    page = request.args.get('page', 1, type=int)
    
    # Create aliases for User table
    student_user = aliased(User, name='student_user')
    teacher_user = aliased(User, name='teacher_user')
    
    # Query students with their results
    students_q = db.session.query(Student, student_user, Group, Teacher, teacher_user, Course)\
        .join(student_user, Student.user_id == student_user.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Teacher, Group.teacher_id == Teacher.id)\
        .join(teacher_user, Teacher.user_id == teacher_user.id)\
        .join(Course, Teacher.course_id == Course.id)\
        .options(db.joinedload(Student.results))

    if current_user.role != 'superadmin':
        students_q = students_q.filter(student_user.branch_id == current_user.branch_id)
    
    pagination = students_q.paginate(page=page, per_page=10, error_out=False)
    students_data = pagination.items
    
    # Format data for template
    students = []
    for student_obj, user_obj, group_obj, teacher_obj, teacher_user_obj, course_obj in students_data:
        students.append({
            'student': student_obj,
            'user': user_obj,
            'group': group_obj,
            'teacher': teacher_obj,
            'teacher_user': teacher_user_obj,
            'course': course_obj
        })
    
    return render_template('admin/students_modern.html', students=students, pagination=pagination)

@app.route('/admin/students/view/<int:student_id>')
@admin_required
def admin_view_student(student_id):
    from sqlalchemy.orm import aliased
    
    student_user = aliased(User, name='student_user')
    teacher_user = aliased(User, name='teacher_user')
    
    student_q = db.session.query(Student, student_user, Group, Teacher, teacher_user, Course)\
        .join(student_user, Student.user_id == student_user.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Teacher, Group.teacher_id == Teacher.id)\
        .join(teacher_user, Teacher.user_id == teacher_user.id)\
        .join(Course, Teacher.course_id == Course.id)\
        .options(db.joinedload(Student.results))\
        .filter(Student.id == student_id)
    if current_user.role != 'superadmin':
        student_q = student_q.filter(student_user.branch_id == current_user.branch_id)
    student = student_q.first_or_404()
    
    # Sort results by date
    results = sorted(student[0].results, key=lambda x: x.submitted_at)
    
    # Prepare chart labels and data
    chart_labels = [r.test.title for r in results]
    chart_data = [r.percentage for r in results]
    
    # Prepare monthly stats
    monthly_stats = {}
    for r in results:
        month_key = r.submitted_at.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = []
        monthly_stats[month_key].append(r.percentage)
    
    monthly_labels = sorted(monthly_stats.keys())
    monthly_data = [sum(monthly_stats[m]) / len(monthly_stats[m]) for m in monthly_labels]
    
    return render_template('admin/view_student_modern.html', 
                         student=student,
                         chart_labels=chart_labels,
                         chart_data=chart_data,
                         monthly_labels=monthly_labels,
                         monthly_data=monthly_data)

@app.route('/admin/results')
@admin_required
def admin_results():
    page = request.args.get('page', 1, type=int)
    results_q = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)
    if current_user.role != 'superadmin':
        results_q = results_q.filter(Group.branch_id == current_user.branch_id)
    pagination = results_q.paginate(page=page, per_page=10, error_out=False)
    results = pagination.items
    return render_template('admin/results_modern.html', results=results, pagination=pagination)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    # Get data for analytics - filtered by branch!
    test_results_q = db.session.query(TestResult, Test, Group)\
        .join(Test, TestResult.test_id == Test.id)\
        .join(Group, Test.group_id == Group.id)
    
    # Filter by branch for non-superadmin
    if current_user.role != 'superadmin':
        test_results_q = test_results_q.filter(Group.branch_id == current_user.branch_id)
    
    test_results = test_results_q.all()
    
    # Prepare data for visualization
    data = []
    group_scores = {}
    pass_count = 0
    fail_count = 0
    
    for result, test, group in test_results:
        data.append({
            'student_name': result.student.user.full_name,
            'group_name': group.name,
            'test_title': test.title,
            'score': result.score,
            'total_questions': result.total_questions,
            'percentage': result.percentage,
            'submitted_at': result.submitted_at
        })
        
        # Group statistics
        if group.name not in group_scores:
            group_scores[group.name] = []
        group_scores[group.name].append(result.percentage)
        
        # Pass/Fail statistics
        if result.percentage >= 60:
            pass_count += 1
        else:
            fail_count += 1
    
    # Generate simple text-based statistics
    charts = {}
    if data:
        # Group averages
        group_averages = {}
        for group_name, scores in group_scores.items():
            group_averages[group_name] = sum(scores) / len(scores)
        
        charts['group_averages'] = group_averages
        charts['pass_fail'] = {'pass': pass_count, 'fail': fail_count}
        charts['total_results'] = len(data)
        charts['average_score'] = sum([d['percentage'] for d in data]) / len(data)
    
    return render_template('admin/analytics_modern.html', charts=charts)

# Teacher Routes
@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    from sqlalchemy.orm import joinedload
    
    try:
        # Check if user has teacher profile
        teacher = db.session.query(Teacher)\
            .options(joinedload(Teacher.user))\
            .options(joinedload(Teacher.course))\
            .filter_by(user_id=current_user.id)\
            .first()
        
        if not teacher:
            logger.warning(f"Teacher profile not found for user {current_user.id}")
            flash('O\'qituvchi profili topilmadi! Admin bilan bog\'laning.', 'danger')
            return redirect(url_for('login'))
        
        # Branch validation for teacher
        if current_user.branch_id != teacher.user.branch_id:
             # Should not happen with decoraters but for perfection:
             flash('Siz ushbu filialga tegishli emassiz.', 'danger')
             return redirect(url_for('logout'))

        groups = db.session.query(Group).options(joinedload(Group.teacher).joinedload(Teacher.course)).filter_by(teacher_id=teacher.id, branch_id=current_user.branch_id).all()
        
        # Har bir guruh uchun o'quvchilar sonini hisoblash
        for group in groups:
            group.count_students = Student.query.filter_by(group_id=group.id).count()
        
        students_count = Student.query.filter(Student.group_id.in_([g.id for g in groups])).count()
        tests_count = Test.query.filter(Test.group_id.in_([g.id for g in groups])).count()
        
        return render_template('teacher/dashboard_modern.html', 
                             groups=groups,
                             students_count=students_count,
                             tests_count=tests_count,
                             teacher=teacher)
    except Exception as e:
        logger.error(f"Error in teacher dashboard: {e}")
        flash('Panelni yuklashda xatolik!', 'danger')
        return redirect(url_for('login'))

# Teacher groups removed - now managed by admin

# Teacher students management removed - now managed by admin

# Teacher tests management removed - now managed by admin

@app.route('/teacher/results')
@teacher_required
def teacher_results():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    groups = Group.query.filter_by(teacher_id=teacher.id).all()
    results = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(Group.teacher_id == teacher.id)\
        .all()
    return render_template('teacher/results_modern.html', results=results)

@app.route('/teacher/group/<int:group_id>')
@teacher_required
def teacher_group_students(group_id):
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    group = Group.query.filter_by(id=group_id, teacher_id=teacher.id).first_or_404()
    
    # Guruhdagi o'quvchilar
    students = db.session.query(Student, User)\
        .join(User, Student.user_id == User.id)\
        .filter(Student.group_id == group_id)\
        .all()
    
    # Guruhdagi testlar
    tests = Test.query.filter_by(group_id=group_id).all()
    
    return render_template('teacher/group_students_modern.html', 
                         group=group, 
                         students=students, 
                         tests=tests)

# Student Routes
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    try:
        student = db.session.query(Student).filter_by(user_id=current_user.id).first()
        if not student:
            flash('O\'quvchi profili topilmadi!', 'danger')
            return redirect(url_for('login'))
        
        # Test results (tugatilgan testlar)
        results = db.session.query(TestResult, Test).join(Test, TestResult.test_id == Test.id).filter(TestResult.student_id == student.id).order_by(TestResult.submitted_at.desc()).all()
        print(f"Test results count: {len(results)}")
        
        # Barcha urinishlarni olish (TestAttempt)
        attempts = TestAttempt.query.filter_by(student_id=student.id, is_submitted=False).all()
        started_test_ids = {a.test_id for a in attempts}
        attempts_map = {a.test_id: a.start_time for a in attempts}
        
        # Tashkent vaqtini olish (get_now helper)
        current_time = get_now()
        
        # Qaysi testlar vaqti tugaganligini aniqlash (individual)
        timed_out_test_ids = set()
        for attempt in attempts:
            test = Test.query.get(attempt.test_id)
            if test:
                # Individual vaqt tugaganmi?
                individual_end_time = attempt.start_time + timedelta(minutes=test.duration_minutes)
                if current_time > individual_end_time:
                    timed_out_test_ids.add(test.id)
        
        # Available tests (mavjud testlar) - Only active ones
        all_tests = Test.query.filter_by(group_id=student.group_id, is_active=True).all()
        completed_test_ids = {result[1].id for result in results}
        available_tests = [test for test in all_tests if test.id not in completed_test_ids]
        print(f"Available tests: {len(available_tests)}, Completed: {len(completed_test_ids)}, Started: {len(started_test_ids)}, Timed Out: {len(timed_out_test_ids)}")
        
        # Calculate average score
        average_score = 0
        if results:
            average_score = sum(result[0].percentage for result in results) / len(results)
        
        # Group outcomes by month for chart
        monthly_stats = {}
        for result, test in results:
            month_key = result.submitted_at.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = []
            monthly_stats[month_key].append(result.percentage)
        
        # Sort months and calculate averages
        months = sorted(monthly_stats.keys())
        monthly_averages = [sum(monthly_stats[m]) / len(monthly_stats[m]) for m in months]
        
        # Create a mapping of test_id -> result object for easier template access
        results_map = {result[1].id: result[0] for result in results}
        
        return render_template('student/dashboard_modern.html', 
                             student=student, 
                             results=results,
                             results_map=results_map,
                             available_tests=available_tests, 
                             completed_test_ids=completed_test_ids, 
                             started_test_ids=started_test_ids,
                             timed_out_test_ids=timed_out_test_ids,
                             attempts_map=attempts_map,
                             current_time=current_time, 
                             average_score=average_score,
                             months=months,
                             monthly_averages=monthly_averages)
    except Exception as e:
        print(f"❌ Error in student dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Panelni yuklashda xatolik: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route('/student/test/<int:test_id>')
@student_required
def student_take_test(test_id):
    student = Student.query.filter_by(user_id=current_user.id).first()
    test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
    
    # Check if student belongs to the test's group and test is active
    if student.group_id != test.group_id or not test.is_active:
        flash('Siz bu testni topshirishga ruxsat etilmagansiz yoki test nofaol.', 'danger')
        return redirect(url_for('student_dashboard'))
    
    # Check if test is within time window
    now = get_now()
    if now < test.start_time:
        flash('Test hali boshlanmagan.', 'warning')
        return redirect(url_for('student_dashboard'))
    elif now > test.end_time:
        flash('Test muddati tugagan.', 'warning')
        return redirect(url_for('student_dashboard'))
    
    # Check if student already took the test
    existing_result = TestResult.query.filter_by(student_id=student.id, test_id=test.id).first()
    if existing_result:
        flash('Siz bu testni allaqachon topshirgansiz.', 'info')
        return redirect(url_for('student_dashboard'))
    
    # Anti-cheat: Record attempt start time
    attempt = TestAttempt.query.filter_by(student_id=student.id, test_id=test.id).first()
    if not attempt:
        attempt = TestAttempt(student_id=student.id, test_id=test.id, start_time=get_now())
        db.session.add(attempt)
        db.session.commit()
    elif attempt.is_submitted:
        flash('Siz bu testni allaqachon topshirgansiz (Attempt finalized).', 'info')
        return redirect(url_for('student_dashboard'))
    
    # Calculate remaining time for the timer synchronization
    now = get_now()
    time_spent_seconds = (now - attempt.start_time).total_seconds()
    total_seconds_allowed = test.duration_minutes * 60
    remaining_seconds = int(max(0, total_seconds_allowed - time_spent_seconds))
    
    # If time is already up before opening, prevent starting
    if remaining_seconds <= 0:
        flash('Test topshirish vaqti tugab bo\'lgan! Siz belgilangan vaqtdan ko\'p sarfladingiz.', 'danger')
        return redirect(url_for('student_dashboard'))

    questions = Question.query.filter_by(test_id=test.id).all()
    return render_template('student/take_test_modern.html', test=test, questions=questions, start_time=attempt.start_time, remaining_seconds=remaining_seconds)

@app.route('/student/test/<int:test_id>/submit', methods=['POST'])
@student_required
def student_submit_test(test_id):
    try:
        student = Student.query.filter_by(user_id=current_user.id).first()
        test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
        
        # Check if student already took the test
        existing_result = TestResult.query.filter_by(student_id=student.id, test_id=test.id).first()
        if existing_result:
            flash('Siz bu testni allaqachon topshirgansiz.', 'danger')
            return redirect(url_for('student_dashboard'))
        
        now = get_now()
        
        if now > test.end_time:
            flash('Testni topshirish muddati tugagan.', 'danger')
            return redirect(url_for('student_dashboard'))
        
        # Anti-cheat check: Duration
        attempt = TestAttempt.query.filter_by(student_id=student.id, test_id=test.id).first()
        if not attempt:
            flash('Test boshlanishi qayd etilmagan! Qayta urinib ko\'ring.', 'danger')
            return redirect(url_for('student_dashboard'))
        
        if attempt.is_submitted:
            flash('Bu test natijasi allaqachon qabul qilingan.', 'warning')
            return redirect(url_for('student_dashboard'))
        
        # Calculate time spent in minutes
        time_diff = now - attempt.start_time
        minutes_spent = time_diff.total_seconds() / 60
        
        # Allow 2 minutes buffer for network delays
        if minutes_spent > (test.duration_minutes + 2):
            error_msg = f'Vaqt tugagan! Test davomiyligi: {test.duration_minutes} daqiqa. Siz {int(minutes_spent)} daqiqa sarfladingiz.'
            logger.warning(f"Time limit exceeded for student {student.user.username}. Spent: {minutes_spent}, Allowed: {test.duration_minutes}")
            flash(error_msg, 'danger')
            return redirect(url_for('student_dashboard'))
        
        # Calculate score
        questions = Question.query.filter_by(test_id=test.id).all()
        
        correct_count = 0
        answers = {}
        
        for question in questions:
            student_answer = request.form.get(f'question_{question.id}')
            answers[str(question.id)] = student_answer
            
            if student_answer == question.correct_answer:
                correct_count += 1
        
        # Calculate percentage
        total_questions = len(questions)
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Handle practical submission
        practical_submission_path = None
        if test.has_practical and 'practical_submission' in request.files:
            file = request.files['practical_submission']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"sub_{student.id}_{test.id}_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                practical_submission_path = filename

        # Create test result
        result = TestResult(
            student_id=student.id,
            test_id=test.id,
            score=correct_count,
            total_questions=total_questions,
            percentage=percentage,
            answers=json.dumps(answers),
            practical_submission=practical_submission_path,
            submitted_at=now
        )
        
        # Mark attempt as finished
        attempt.is_submitted = True
        
        db.session.add(result)
        db.session.commit()
        
        flash(f'Test muvaffaqiyatli topshirildi! Ballingiz: {correct_count}/{len(questions)} ({result.percentage:.1f}%)', 'success')
        
        return redirect(url_for('student_dashboard'))
        
    except Exception as e:
        logger.error(f"Error in test submit: {e}")
        flash(f'Testni topshirishda xatolik: {str(e)}', 'danger')
        return redirect(url_for('student_dashboard'))

# ==================== PRACTICAL SUBMISSION ROUTES ====================

@app.route('/admin/test/<int:test_id>/practical-submissions')
@admin_required
def admin_practical_submissions(test_id):
    test = Test.query.filter_by(id=test_id, branch_id=current_user.branch_id).first_or_404()
    
    submissions = db.session.query(TestResult, Student, User)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .filter(TestResult.test_id == test_id)\
        .filter(TestResult.practical_submission != None)\
        .order_by(TestResult.submitted_at.desc())\
        .all()
    
    # Also get students who haven't submitted practical yet
    all_results = db.session.query(TestResult, Student, User)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .filter(TestResult.test_id == test_id)\
        .order_by(TestResult.submitted_at.desc())\
        .all()
    
    graded_count = sum(1 for r, s, u in all_results if r.practical_score is not None)
    pending_count = sum(1 for r, s, u in all_results if r.practical_submission and r.practical_score is None)
    
    return render_template('admin/practical_submissions.html',
                           test=test,
                           all_results=all_results,
                           graded_count=graded_count,
                           pending_count=pending_count)

@app.route('/admin/result/<int:result_id>/grade-practical', methods=['POST'])
@admin_required
def admin_grade_practical(result_id):
    result = TestResult.query.get_or_404(result_id)
    
    # Security check
    test = Test.query.filter_by(id=result.test_id, branch_id=current_user.branch_id).first_or_404()
    
    score = request.form.get('practical_score', type=int)
    feedback = request.form.get('practical_feedback', '').strip()
    
    if score is None or not (0 <= score <= 100):
        flash('Ball 0 dan 100 gacha bo\'lishi kerak!', 'danger')
        return redirect(url_for('admin_practical_submissions', test_id=result.test_id))
    
    result.practical_score = score
    result.practical_feedback = feedback
    db.session.commit()
    
    flash(f'✅ {result.student.user.full_name} ning amaliy ishi {score}/100 ball bilan baholandi!', 'success')
    return redirect(url_for('admin_practical_submissions', test_id=result.test_id))

# PDF Export Routes
@app.route('/admin/results/pdf/<int:result_id>')
@admin_required
def admin_export_result_pdf(result_id):
    # ... existing implementation ...
    result = TestResult.query.get_or_404(result_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Test Natijasi Hisoboti")
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"O'quvchi: {result.student.user.full_name}")
    p.drawString(100, 680, f"Guruh: {result.student.group.name}")
    p.drawString(100, 660, f"Test: {result.test.title}")
    p.drawString(100, 620, f"Ball: {result.score}/{result.total_questions}")
    p.drawString(100, 600, f"Foiz: {result.percentage:.1f}%")
    p.drawString(100, 580, f"Sana: {result.submitted_at.strftime('%Y-%m-%d %H:%M')}")
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'natija_{result.id}.pdf', mimetype='application/pdf')

@app.route('/admin/result/<int:result_id>')
@admin_required
def admin_result_detail(result_id):
    import ast
    result_q = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(TestResult.id == result_id)
    if current_user.role != 'superadmin':
        result_q = result_q.filter(Group.branch_id == current_user.branch_id)
    result = result_q.first_or_404()
    
    result_obj, student_obj, user_obj, group_obj, test_obj = result
    
    # Parse answers
    try:
        student_answers = json.loads(result_obj.answers)
    except:
        try:
            import ast
            student_answers = ast.literal_eval(result_obj.answers)
        except:
            student_answers = {}
        
    questions = Question.query.filter_by(test_id=test_obj.id).all()
    
    return render_template('admin/result_detail_modern.html', 
                         result=result_obj, 
                         student=student_obj, 
                         user=user_obj, 
                         group=group_obj, 
                         test=test_obj,
                         questions=questions,
                         answers=student_answers)

@app.route('/teacher/result/<int:result_id>')
@teacher_required
def teacher_result_detail(result_id):
    import ast
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    result = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(TestResult.id == result_id, Group.teacher_id == teacher.id).first_or_404()
    
    result_obj, student_obj, user_obj, group_obj, test_obj = result
    
    # Parse answers
    try:
        student_answers = json.loads(result_obj.answers)
    except:
        try:
            import ast
            student_answers = ast.literal_eval(result_obj.answers)
        except:
            student_answers = {}
        
    questions = Question.query.filter_by(test_id=test_obj.id).all()
    
    return render_template('admin/result_detail_modern.html', 
                         result=result_obj, 
                         student=student_obj, 
                         user=user_obj, 
                         group=group_obj, 
                         test=test_obj,
                         questions=questions,
                         answers=student_answers,
                         is_teacher=True)

@app.route('/teacher/results/pdf/<int:result_id>')
@teacher_required
def teacher_export_result_pdf(result_id):
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    result = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(TestResult.id == result_id, Group.teacher_id == teacher.id)\
        .first_or_404()
    result_obj, student_obj, user_obj, group_obj, test_obj = result
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Test Result Report")
    
    # Student Information
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"Student: {user_obj.full_name}")
    p.drawString(100, 680, f"Group: {group_obj.name}")
    p.drawString(100, 660, f"Test: {test_obj.title}")
    
    # Score Information
    p.drawString(100, 620, f"Score: {result_obj.score}/{result_obj.total_questions}")
    p.drawString(100, 600, f"Percentage: {result_obj.percentage:.1f}%")
    p.drawString(100, 580, f"Submitted: {result_obj.submitted_at.strftime('%Y-%m-%d %H:%M')}")
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'result_{result_obj.id}.pdf', mimetype='application/pdf')

@app.route('/teacher/group/<int:group_id>/pdf')
@teacher_required
def teacher_export_group_pdf(group_id):
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    group = Group.query.filter_by(id=group_id, teacher_id=teacher.id).first_or_404()
    
    results = db.session.query(TestResult, Student, User, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(Student.group_id == group_id)\
        .all()
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 50, f"{group.name} Guruxi Natijalari")
    
    # Headers
    p.setFont("Helvetica-Bold", 10)
    y = height - 100
    p.drawString(50, y, "O'quvchi")
    p.drawString(250, y, "Test")
    p.drawString(400, y, "Ball")
    p.drawString(450, y, "Foiz")
    p.drawString(500, y, "Sana")
    
    p.line(50, y-5, 550, y-5)
    y -= 20
    
    p.setFont("Helvetica", 9)
    for res_obj, student_obj, user_obj, test_obj in results:
        if y < 50:
            p.showPage()
            p.setFont("Helvetica-Bold", 10)
            y = height - 50
            p.drawString(50, y, "O'quvchi")
            p.drawString(250, y, "Test")
            p.drawString(400, y, "Ball")
            p.drawString(450, y, "Foiz")
            p.drawString(500, y, "Sana")
            p.line(50, y-5, 550, y-5)
            y -= 20
            p.setFont("Helvetica", 9)
            
        p.drawString(50, y, user_obj.full_name)
        p.drawString(250, y, test_obj.title[:30])
        p.drawString(400, y, f"{res_obj.score}/{res_obj.total_questions}")
        p.drawString(450, y, f"{res_obj.percentage:.1f}%")
        p.drawString(500, y, res_obj.submitted_at.strftime('%Y-%m-%d'))
        y -= 15
        
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'guruh_natija_{group.name}.pdf', mimetype='application/pdf')

@app.route('/student/results/pdf/<int:result_id>')
@student_required
def student_download_result_pdf(result_id):
    student = Student.query.filter_by(user_id=current_user.id).first()
    result = TestResult.query.filter_by(id=result_id, student_id=student.id).first_or_404()
    
    # Parse answers
    try:
        student_answers = ast.literal_eval(result.answers)
    except:
        student_answers = {}
        
    questions = Question.query.filter_by(test_id=result.test.id).all()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Test Natijasi (O'quvchi)", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Information
    status = "O'tdim" if result.percentage >= 60 else "O'tmadim"
    info_text = f"""
    <b>O'quvchi:</b> {current_user.full_name}<br/>
    <b>Guruh:</b> {student.group.name}<br/>
    <b>Test:</b> {result.test.title}<br/>
    <b>Ball:</b> {result.score}/{result.total_questions}<br/>
    <b>Foiz:</b> {result.percentage:.1f}%<br/>
    <b>Sana:</b> {result.submitted_at.strftime('%Y-%m-%d %H:%M')}<br/>
    <b>Holat:</b> {status}
    """
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Questions Table
    data = [['#', 'Savol', 'Sizning javobingiz', 'Holat']]
    
    for i, q in enumerate(questions, 1):
        ans = student_answers.get(str(q.id), "-")
        is_correct = "To'g'ri" if ans == q.correct_answer else "Noto'g'ri"
        
        # Add a Paragraph for question to handle wrapping
        q_para = Paragraph(q.question_text, styles['Normal'])
        data.append([str(i), q_para, ans, is_correct])
        
    table = Table(data, colWidths=[30, 300, 100, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
    ]))
    
    # Add colors for Correct/Incorrect
    for i in range(1, len(data)):
        if data[i][3] == "To'g'ri":
            table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), colors.green)]))
        else:
            table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), colors.red)]))
            
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'natija_{result.id}.pdf', mimetype='application/pdf')

@app.route('/student/results')
@student_required
def student_results():
    student = Student.query.filter_by(user_id=current_user.id).first()
    results = db.session.query(TestResult, Test).join(Test, TestResult.test_id == Test.id).filter(TestResult.student_id == student.id).order_by(TestResult.submitted_at.desc()).all()
    return render_template('student/results_modern.html', results=results, student=student)

# --- New Admin PDF Exports ---

@app.route('/admin/export/students')
@admin_required
def admin_export_students():
    from sqlalchemy.orm import aliased
    student_user = aliased(User, name='student_user')
    teacher_user = aliased(User, name='teacher_user')
    
    students_data = db.session.query(Student, student_user, Group, Teacher, teacher_user, Course)\
        .join(student_user, Student.user_id == student_user.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Teacher, Group.teacher_id == Teacher.id)\
        .join(teacher_user, Teacher.user_id == teacher_user.id)\
        .join(Course, Teacher.course_id == Course.id)\
        .filter(Group.branch_id == current_user.branch_id)\
        .all()
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Barcha O'quvchilar Ro'yxati", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['#', 'F.I.SH', 'Login', 'Guruh', 'Kurs', "O'qituvchi"]]
    for i, (student, user, group, teacher, t_user, course) in enumerate(students_data, 1):
        data.append([
            str(i),
            user.full_name,
            user.username,
            group.name,
            course.name,
            t_user.full_name
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#607d8b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='barcha_oquvchilar.pdf', mimetype='application/pdf')

@app.route('/admin/export/results')
@admin_required
def admin_export_results():
    results = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(Group.branch_id == current_user.branch_id)\
        .order_by(TestResult.submitted_at.desc())\
        .all()
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Umumiy Natijalar Ro'yxati", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['#', "O'quvchi", 'Guruh', 'Test', 'Ball', 'Foiz', 'Sana']]
    for i, (res, st, usr, grp, tst) in enumerate(results, 1):
        data.append([
            str(i),
            usr.full_name,
            grp.name,
            tst.title,
            f"{res.score}/{res.total_questions}",
            f"{res.percentage:.1f}%",
            res.submitted_at.strftime('%Y-%m-%d')
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='umumiy_natijalar.pdf', mimetype='application/pdf')

@app.route('/admin/export/group_results/<int:group_id>')
@admin_required
def admin_export_group_results(group_id):
    group = Group.query.filter_by(id=group_id, branch_id=current_user.branch_id).first_or_404()
    results = db.session.query(TestResult, Student, User, Group, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Group, Student.group_id == Group.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(Group.id == group_id)\
        .order_by(TestResult.submitted_at.desc())\
        .all()
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph(f"'{group.name}' guruhi Natijalari", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['#', "O'quvchi", 'Test', 'Ball', 'Foiz', 'Sana']]
    for i, (res, st, usr, grp, tst) in enumerate(results, 1):
        data.append([
            str(i),
            usr.full_name,
            tst.title,
            f"{res.score}/{res.total_questions}",
            f"{res.percentage:.1f}%",
            res.submitted_at.strftime('%Y-%m-%d')
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9c27b0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'{group.name}_natijalari.pdf', mimetype='application/pdf')

@app.context_processor
def inject_admin_groups():
    if current_user.is_authenticated and current_user.role == 'admin':
        try:
            groups = Group.query.all()
            return dict(admin_groups=groups)
        except:
            return dict(admin_groups=[])
    return dict()

@app.route('/admin/groups/view/<int:group_id>')
@admin_required
def admin_view_group(group_id):
    group = Group.query.filter_by(id=group_id, branch_id=current_user.branch_id).first_or_404()
    teacher = db.session.query(Teacher, User).join(User).filter(Teacher.id == group.teacher_id).first()
    students = db.session.query(Student, User).join(User).filter(Student.group_id == group.id).all()
    tests = Test.query.filter_by(group_id=group.id).all()
    
    results = db.session.query(TestResult, Student, User, Test)\
        .join(Student, TestResult.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .join(Test, TestResult.test_id == Test.id)\
        .filter(Student.group_id == group.id)\
        .order_by(TestResult.submitted_at.desc())\
        .all()
        
    average_score = sum(r[0].percentage for r in results) / len(results) if results else 0
    if average_score >= 86:
        group_level = "A'lo"
    elif average_score >= 71:
        group_level = "Yaxshi"
    elif average_score >= 56:
        group_level = "Qoniqarli"
    else:
        group_level = "Qoniqarsiz" if results else "Natijalar yo'q"
    
    return render_template('admin/view_group_modern.html', 
                         group=group, 
                         teacher=teacher, 
                         students=students, 
                         tests=tests,
                         results=results,
                         average_score=average_score,
                         group_level=group_level)

@app.route('/superadmin/branches', methods=['GET', 'POST'])
@superadmin_required
def superadmin_branches():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) < 2:
            flash("Filial nomi kamida 2 belgidan iborat bo'lishi kerak!", "danger")
        else:
            branch = Branch(name=name)
            db.session.add(branch)
            db.session.commit()
            flash(f"'{name}' filiali muvaffaqiyatli qo'shildi!", "success")
        return redirect(url_for('superadmin_branches'))
    
    branches = Branch.query.all()
    return render_template('admin/branches_modern.html', branches=branches)

@app.route('/superadmin/branches/delete/<int:branch_id>', methods=['POST'])
@superadmin_required
def superadmin_delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    # Check if branch has users
    if User.query.filter_by(branch_id=branch_id).first():
        flash("Ushbu filialda foydalanuvchilar bor. Oldin ularni o'chiring!", "danger")
    else:
        db.session.delete(branch)
        db.session.commit()
        flash(f"'{branch.name}' filiali o'chirildi!", "success")
    return redirect(url_for('superadmin_branches'))

@app.route('/superadmin/branches/edit/<int:branch_id>', methods=['GET', 'POST'])
@superadmin_required
def superadmin_edit_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) < 2:
            flash("Filial nomi kamida 2 belgidan iborat bo'lishi kerak!", "danger")
        else:
            branch.name = name
            db.session.commit()
            flash(f"'{name}' filiali muvaffaqiyatli yangilandi!", "success")
        return redirect(url_for('superadmin_branches'))
    return render_template('superadmin/edit_branch_modern.html', branch=branch)

@app.route('/superadmin/admins', methods=['GET'])
@superadmin_required
def superadmin_admins():
    admins = User.query.filter_by(role='admin').all()
    branches = Branch.query.all()
    return render_template('superadmin/admins_modern.html', admins=admins, branches=branches)

@app.route('/superadmin/admins/add', methods=['GET', 'POST'])
@superadmin_required
def superadmin_add_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        branch_id = request.form.get('branch_id')
        
        if not username or not password or not full_name or not branch_id:
            flash("Barcha maydonlarni to'ldiring!", "danger")
            return redirect(url_for('superadmin_add_admin'))
        
        # Check if username already exists in the branch
        if User.query.filter_by(username=username, branch_id=branch_id).first():
            flash("Ushbu filialdagi login allaqachon mavjud!", "danger")
            return redirect(url_for('superadmin_add_admin'))
        
        # Check if branch already has an admin
        existing_admin = User.query.filter_by(role='admin', branch_id=branch_id).first()
        if existing_admin:
            flash(f"Ushbu filialda allaqachon admin bor: {existing_admin.full_name}. Oldin eski adminni o'chiring!", "warning")
            return redirect(url_for('superadmin_add_admin'))
        
        admin_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='admin',
            full_name=full_name,
            branch_id=int(branch_id)
        )
        db.session.add(admin_user)
        db.session.commit()
        
        branch = Branch.query.get(branch_id)
        flash(f"'{full_name}' admin sifatida '{branch.name}' filialiga tayinlandi!", "success")
        return redirect(url_for('superadmin_admins'))
    
    branches = Branch.query.all()
    # Get branches that already have admins
    branches_with_admin = set()
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        if admin.branch_id:
            branches_with_admin.add(admin.branch_id)
    
    return render_template('superadmin/add_admin_modern.html', branches=branches, branches_with_admin=branches_with_admin)

@app.route('/superadmin/admins/edit/<int:admin_id>', methods=['GET', 'POST'])
@superadmin_required
def superadmin_edit_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first_or_404()
    if request.method == 'POST':
        admin.full_name = request.form.get('full_name')
        admin.username = request.form.get('username')
        new_branch_id = request.form.get('branch_id')
        
        password = request.form.get('password')
        if password:
            admin.password_hash = generate_password_hash(password)
        
        if new_branch_id:
            admin.branch_id = int(new_branch_id)
        
        db.session.commit()
        flash(f"Admin '{admin.full_name}' ma'lumotlari yangilandi!", "success")
        return redirect(url_for('superadmin_admins'))
    
    branches = Branch.query.all()
    return render_template('superadmin/edit_admin_modern.html', admin=admin, branches=branches)

@app.route('/superadmin/admins/delete/<int:admin_id>', methods=['POST'])
@superadmin_required
def superadmin_delete_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first_or_404()
    name = admin.full_name
    db.session.delete(admin)
    db.session.commit()
    flash(f"Admin '{name}' muvaffaqiyatli o'chirildi!", "success")
    return redirect(url_for('superadmin_admins'))

@app.route('/superadmin/settings', methods=['GET', 'POST'])
@superadmin_required
def superadmin_settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(current_user.password_hash, old_password):
                flash("Eski parol noto'g'ri!", "danger")
            elif new_password != confirm_password:
                flash("Yangi parollar mos kelmaydi!", "danger")
            elif len(new_password) < 4:
                flash("Parol kamida 4 belgidan iborat bo'lishi kerak!", "danger")
            else:
                current_user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash("Parol muvaffaqiyatli o'zgartirildi!", "success")
        
        elif action == 'update_profile':
            full_name = request.form.get('full_name')
            if full_name and len(full_name) >= 2:
                current_user.full_name = full_name
                db.session.commit()
                flash("Profil ma'lumotlari yangilandi!", "success")
            else:
                flash("Ism kamida 2 belgidan iborat bo'lishi kerak!", "danger")
        
        return redirect(url_for('superadmin_settings'))
    
    # Tizim statistikasi
    stats = {
        'total_branches': Branch.query.count(),
        'total_admins': User.query.filter_by(role='admin').count(),
        'total_teachers': Teacher.query.count(),
        'total_students': Student.query.count(),
        'total_tests': Test.query.count(),
        'total_results': TestResult.query.count(),
    }
    
    return render_template('superadmin/settings_modern.html', stats=stats)


# ==================== AI CHATBOT ====================

def truncate_context(text, max_chars=2500):
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    if "\n" in truncated:
        truncated = truncated.rsplit("\n", 1)[0]
    return truncated + "\n... [Kontekst qisqartirildi]"


def get_system_context(user):
    """Bazadan foydalanuvchi roliga qarab qisqartirilgan kontekst yig'adi"""
    context_parts = []

    total_courses = Course.query.count()
    if total_courses:
        context_parts.append("=== KURS BILAN BOG'LIQ MA'LUMOT ===")
        context_parts.append(f"Jami kurslar: {total_courses}")
        course_names = [c.name for c in Course.query.limit(8).all()]
        for name in course_names:
            context_parts.append(f"- {name}")
        if total_courses > 8:
            context_parts.append(f"... va {total_courses - 8} ta boshqa kurs mavjud")
        context_parts.append("")

    if user.role == 'superadmin':
        branches = Branch.query.all()
        context_parts.append("=== SUPERADMIN STATISTIKASI ===")
        context_parts.append(f"Filiallar: {len(branches)}")
        for b in branches:
            students_count = User.query.filter_by(branch_id=b.id, role='student').count()
            teachers_count = User.query.filter_by(branch_id=b.id, role='teacher').count()
            admin = User.query.filter_by(branch_id=b.id, role='admin').first()
            admin_name = admin.full_name if admin else "Tayinlanmagan"
            context_parts.append(f"{b.name}: O'quvchilar {students_count}, O'qituvchilar {teachers_count}, Admin {admin_name}")

        context_parts.append("")
        context_parts.append(f"Jami testlar: {Test.query.count()}")
        context_parts.append(f"Jami natijalar: {TestResult.query.count()}")

        # Optimization: Limit groups to process only first 3 to prevent OOM
        groups = Group.query.limit(3).all()
        for g in groups:
            res_count = db.session.query(TestResult).join(Student).filter(Student.group_id == g.id).count()
            if res_count > 0:
                # Get last 5 avg to keep it fast
                recent = db.session.query(TestResult.percentage).join(Student).filter(Student.group_id == g.id).limit(20).all()
                avg = sum(r[0] for r in recent) / len(recent)
                context_parts.append(f"Guruh {g.name} (B{g.branch_id}): O'rtacha {avg:.1f}% (Oxirgi 20 ta), Jami {res_count}")

    elif user.role == 'admin':
        branch_id = user.branch_id
        branch = Branch.query.get(branch_id)
        context_parts.append(f"=== ADMIN PANEL: {branch.name if branch else 'Noma\'lum'} filiali ===")

        st_count = db.session.query(Student).join(User).filter(User.branch_id == branch_id).count()
        tr_count = db.session.query(Teacher).join(User).filter(User.branch_id == branch_id).count()
        gr_count = Group.query.filter_by(branch_id=branch_id).count()

        context_parts.append(f"O'quvchilar: {st_count}")
        context_parts.append(f"O'qituvchilar: {tr_count}")
        context_parts.append(f"Guruhlar: {gr_count}")

        tests = Test.query.filter_by(branch_id=branch_id).limit(5).all()
        context_parts.append(f"Testlar: {Test.query.filter_by(branch_id=branch_id).count()}")
        if tests:
            context_parts.append("Oxirgi 5 test:")
            for t in tests:
                q_count = Question.query.filter_by(test_id=t.id).count()
                context_parts.append(f"- {t.title} | {q_count} savol")

        groups = Group.query.filter_by(branch_id=branch_id).limit(5).all()
        for g in groups:
            res_count = db.session.query(TestResult).join(Student).filter(Student.group_id == g.id).count()
            teacher = db.session.query(User).join(Teacher).filter(Teacher.id == g.teacher_id).first()
            teacher_name = teacher.full_name if teacher else "Noma'lum"
            if res_count > 0:
                recent = db.session.query(TestResult.percentage).join(Student).filter(Student.group_id == g.id).limit(10).all()
                avg = sum(r[0] for r in recent) / len(recent)
                context_parts.append(f"G {g.name}: O'rtacha {avg:.1f}%, Natijalar {res_count}")
            else:
                context_parts.append(f"Guruh {g.name} ({teacher_name}): Hali natijalar yo'q")

    elif user.role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if teacher:
            course = Course.query.get(teacher.course_id)
            context_parts.append(f"=== O'QITUVCHI: {user.full_name} | Kurs: {course.name if course else 'Noma\'lum'} ===")

            groups = Group.query.filter_by(teacher_id=teacher.id).all()
            context_parts.append(f"Guruhlar: {len(groups)}")
            for g in groups[:5]:
                st_count = db.session.query(Student).filter_by(group_id=g.id).count()
                g_tests_count = Test.query.filter_by(group_id=g.id).count()
                context_parts.append(f"- {g.name}: {st_count} o'quvchi, Testlar: {g_tests_count}")

            if groups:
                tested_results = TestResult.query.join(Student).filter(Student.group_id.in_([g.id for g in groups])).all()
                if tested_results:
                    avg = sum(r.percentage for r in tested_results) / len(tested_results)
                    context_parts.append(f"Guruhlar bo'yicha o'rtacha ball: {avg:.1f}%")

    elif user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            group = Group.query.get(student.group_id)
            teacher = db.session.query(User).join(Teacher).filter(Teacher.id == group.teacher_id).first() if group else None

            context_parts.append(f"=== O'QUVCHI: {user.full_name} ===")
            if group:
                context_parts.append(f"Guruh: {group.name}")
            if teacher:
                context_parts.append(f"O'qituvchi: {teacher.full_name}")

            results = TestResult.query.filter_by(student_id=student.id).order_by(TestResult.submitted_at.desc()).all()
            if results:
                avg = sum(r.percentage for r in results) / len(results)
                context_parts.append(f"- Jami topshirilgan testlar: {len(results)}")
                context_parts.append(f"- O'rtacha foiz: {avg:.1f}%")
                context_parts.append("Oxirgi 5 ta natija:")
                for r in results[:5]:
                    test = Test.query.get(r.test_id)
                    context_parts.append(f"  • {test.title if test else '?'}: {r.score}/{r.total_questions} ({r.percentage:.1f}%) — {r.submitted_at.strftime('%Y-%m-%d')}")
            else:
                context_parts.append("Siz hali birorta ham test topshirmagansiz. O'qishda omad!")

    return truncate_context("\n".join(context_parts))


@app.route('/api/chat', methods=['POST'])

@login_required
@csrf.exempt
def api_chat():
    """AI Chatbot API endpoint with Multi-Engine support"""
    if not gemini_model and not groq_client:
        return jsonify({
            'error': "AI chatbot sozlanmagan.", 
            'response': "⚠️ AI chatbot hozircha ishlamaydi. Administrator API kalitlarni sozlashi kerak."
        }), 200
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Xabar bo\'sh'}), 400
        
        # Collect system context
        context = get_system_context(current_user)
        context = truncate_context(context, max_chars=2200)
        
        role_names = {
            'superadmin': 'Super Admin (Barcha filiallarni boshqaruvchi)',
            'admin': 'Filial Admini',
            'teacher': "O'qituvchi",
            'student': "O'quvchi"
        }
        
        system_prompt = f"""Sen "Joylinks IT Ta'lim Tizimi" platformasining professional AI yordamchisisn. Noming "JoyBot".
Vazifang: Foydalanuvchilarga tizimdan foydalanishda, natijalarni tahlil qilishda va o'qishda yordam berish.

Xaraktering: Professional, samimiy, motivatsiya beruvchi va har doim aniq ma'lumot beruvchi.

FOYDALANUVCHI MA'LUMOTLARI:
- Ism: {current_user.full_name}
- Rol: {role_names.get(current_user.role, current_user.role)}
{f"- Filial: {current_user.branch.name}" if current_user.branch else ""}

=== TIZIMDAGI JORIY HOLAT (BAZADAN MA'LUMOT) ===
{context}
===

QOIDALAR:
1. FAQAT O'zbek tilida javob ber.
2. Har doim samimiy va hurmat bilan gaplash (Sizlab).
3. Tizim ma'lumotlari so'ralganda (masalan: "nechta o'quvchim bor?", "natijam qanday?") yuqoridagi "BAZADAN MA'LUMOT" bo'limiga tayanib ANIQ RAQAMLAR keltir.
4. Agar foydalanuvchi so'ragan ma'lumot bazada yo'q bo'lsa, "Kechirasiz, tizimda bu haqda ma'lumot topmadim" deb to'g'risini ayt.
5. O'quvchilarga motivatsiya ber, xatolarini tushuntirib berishga harakat qil.
6. Javoblarda mos keladigan emoji'lardan foydalan.
7. Qisqa va lo'nda javob berishga harakat qil, foydalanuvchini charchatma.
8. Xavfsizlik: Boshqa foydalanuvchilarning parollarini yoki shaxsiy ma'lumotlarini hech qachon oshkor qilma."""

        ai_response = None
        last_error = None

        # 1. Try Groq (Llama 3.1 70B) if configured - Best performance/speed
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                ai_response = response.choices[0].message.content
                logger.info("✅ Answered via Groq (Llama 3.3)")
            except Exception as e:
                logger.warning(f"⚠️ Groq attempt failed: {e}")
                last_error = e

        # 2. Fallback to Gemini if Groq failed or not configured
        if not ai_response and gemini_model:
            for attempt in range(2):
                try:
                    full_input = f"{system_prompt}\n\nFoydalanuvchi: {user_message}"
                    response = gemini_model.generate_content(full_input)
                    if response.text:
                        ai_response = response.text
                        logger.info("✅ Answered via Gemini")
                        break
                except Exception as e:
                    last_error = e
                    logger.warning(f"⚠️ Gemini attempt {attempt+1} failed: {e}")
                    if "429" in str(e):
                        time.sleep(2)  # Short wait for rate limit

        if ai_response:
            return jsonify({'response': ai_response})
        else:
            error_msg = str(last_error) if last_error else 'Unknown error'
            if '429' in error_msg or 'quota' in error_msg.lower():
                return jsonify({
                    'response': "⏳ AI hozir juda band (Bepul API cheklovi). Iltimos, 1 daqiqadan so'ng qayta urinib ko'ring yoki Groq API kalitini kiritishni maslahat beraman."
                }), 200
            return jsonify({'response': "😔 Kechirasiz, xizmatda vaqtinchalik uzilish yuz berdi. Birozgacha keyin qayta urinib ko'ring."}), 200
    
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': f"⚠️ Xatolik yuz berdi: {str(e)[:100]}"}), 200


@app.errorhandler(413)
def file_too_large(e):
    flash('⚠️ Fayl juda katta! Faylingiz 7 MB dan kichik bo\'lishi kerak. Iltimos, faylni kichiklashtiring va qayta yuklang.', 'danger')
    return redirect(request.referrer or url_for('student_dashboard'))

@app.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Qat'iy Production sozlamalari
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000)),
        debug=False,  # Debug o'chirildi
        threaded=True
    )
