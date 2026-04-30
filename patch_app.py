import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Dashboard counts
content = re.sub(
    r'total_students = Student\.query\.count\(\)',
    r'total_students = Student.query.join(User).filter(User.branch_id == current_user.branch_id).count()',
    content
)
content = re.sub(
    r'total_teachers = Teacher\.query\.count\(\)',
    r'total_teachers = Teacher.query.join(User).filter(User.branch_id == current_user.branch_id).count()',
    content
)
content = re.sub(
    r'total_courses = Course\.query\.count\(\)',
    r'total_courses = Course.query.filter_by(branch_id=current_user.branch_id).count()',
    content
)
content = re.sub(
    r'total_tests = Test\.query\.count\(\)',
    r'total_tests = Test.query.filter_by(branch_id=current_user.branch_id).count()',
    content
)
content = re.sub(
    r'total_groups = Group\.query\.count\(\)',
    r'total_groups = Group.query.filter_by(branch_id=current_user.branch_id).count()',
    content
)

# 2. Add branch_id to Course and Group creates
content = re.sub(
    r'course = Course\(name=name, description=description\)',
    r'course = Course(name=name, description=description, branch_id=current_user.branch_id)',
    content
)
content = re.sub(
    r'group = Group\(name=name, teacher_id=teacher_id\)',
    r'group = Group(name=name, teacher_id=teacher_id, branch_id=current_user.branch_id)',
    content
)
content = re.sub(
    r'test = Test\(\s*title=title,\s*group_id=group_id,\s*start_time=start_time,\s*end_time=end_time,\s*duration_minutes=duration_minutes\s*\)',
    r'test = Test(title=title, group_id=group_id, start_time=start_time, end_time=end_time, duration_minutes=duration_minutes, branch_id=current_user.branch_id)',
    content
)

# 3. get_or_404 -> filter_by(id=..., branch_id=...).first_or_404()
content = re.sub(
    r'Course\.query\.get_or_404\((.*?)\)',
    r'Course.query.filter_by(id=\1, branch_id=current_user.branch_id).first_or_404()',
    content
)
content = re.sub(
    r'Group\.query\.get_or_404\((.*?)\)',
    r'Group.query.filter_by(id=\1, branch_id=current_user.branch_id).first_or_404()',
    content
)
content = re.sub(
    r'Test\.query\.get_or_404\((.*?)\)',
    r'Test.query.filter_by(id=\1, branch_id=current_user.branch_id).first_or_404()',
    content
)

# User queries (Students, Teachers, Admins)
# For users it is better to `.filter_by(branch_id=current_user.branch_id).first_or_404()` but wait, students might be implicitly via User.
content = re.sub(
    r'User\.query\.get_or_404\((.*?)\)',
    r'User.query.filter_by(id=\1, branch_id=current_user.branch_id).first_or_404()',
    content
)

# 4. Filter all() queries
content = re.sub(
    r'courses = Course\.query\.all\(\)',
    r'courses = Course.query.filter_by(branch_id=current_user.branch_id).all()',
    content
)
# admin_groups
content = re.sub(
    r'groups = db\.session\.query\(Group, Teacher, User, Course\)\.join\(Teacher, Group\.teacher_id == Teacher\.id\)\.join\(User, Teacher\.user_id == User\.id\)\.join\(Course, Teacher\.course_id == Course\.id\)\.all\(\)',
    r'groups = db.session.query(Group, Teacher, User, Course).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).join(Course, Teacher.course_id == Course.id).filter(Group.branch_id == current_user.branch_id).all()',
    content
)
# admin_tests
content = re.sub(
    r'tests = db\.session\.query\(Test, Group, Teacher, User\)\.join\(Group, Test\.group_id == Group\.id\)\.join\(Teacher, Group\.teacher_id == Teacher\.id\)\.join\(User, Teacher\.user_id == User\.id\)\.all\(\)',
    r'tests = db.session.query(Test, Group, Teacher, User).join(Group, Test.group_id == Group.id).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()',
    content
)
# admin_users
content = re.sub(
    r'teachers = db\.session\.query\(Teacher, User, Course\)\.join\(User\)\.join\(Course\)\.all\(\)',
    r'teachers = db.session.query(Teacher, User, Course).join(User).join(Course).filter(User.branch_id == current_user.branch_id).all()',
    content
)
content = re.sub(
    r'groups = db\.session\.query\(Group, Teacher, User\)\.join\(Teacher, Group\.teacher_id == Teacher\.id\)\.join\(User, Teacher\.user_id == User\.id\)\.all\(\)',
    r'groups = db.session.query(Group, Teacher, User).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).filter(Group.branch_id == current_user.branch_id).all()',
    content
)
# students list
content = re.sub(
    r'student_users = User\.query\.filter_by\(role=\'student\'\)\.all\(\)',
    r'student_users = User.query.filter_by(role=\'student\', branch_id=current_user.branch_id).all()',
    content
)
# teachers list
content = re.sub(
    r'users = User\.query\.filter_by\(role=\'teacher\'\)\.all\(\)',
    r'users = User.query.filter_by(role=\'teacher\', branch_id=current_user.branch_id).all()',
    content
)
# admin_students queries
content = re.sub(
    r'students = db\.session\.query\(Student, User, Group\)\.join\(User\)\.join\(Group\)\.all\(\)',
    r'students = db.session.query(Student, User, Group).join(User).join(Group).filter(User.branch_id == current_user.branch_id).all()',
    content
)

# For student and teacher logins:
# A teacher or student should only see their tests, but tests already belong to group, and group to branch. So their queries might already be isolated. 

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py successfully patched.")
