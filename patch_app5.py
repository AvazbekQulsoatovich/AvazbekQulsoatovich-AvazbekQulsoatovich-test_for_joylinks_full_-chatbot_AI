import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update admin_required to allow superadmin
text = re.sub(
    r"if not current_user\.is_authenticated or current_user\.role != 'admin':",
    r"if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:",
    text
)

# 2. Update Courses query
text = re.sub(
    r"courses = Course\.query\.filter_by\(branch_id=current_user\.branch_id\)\.all\(\)",
    r"courses = Course.query.all() if current_user.role == 'superadmin' else Course.query.filter_by(branch_id=current_user.branch_id).all()",
    text
)

# 3. Update Teachers query
text = re.sub(
    r"teachers = db\.session\.query\(Teacher, User, Course\)\.join\(User\)\.join\(Course\)\.filter\(User\.branch_id == current_user\.branch_id\)\.all\(\)",
    r"teachers_q = db.session.query(Teacher, User, Course).join(User).join(Course)\n    if current_user.role != 'superadmin':\n        teachers_q = teachers_q.filter(User.branch_id == current_user.branch_id)\n    teachers = teachers_q.all()",
    text
)

# 4. Update Groups query
text = re.sub(
    r"groups = db\.session\.query\(Group, Teacher, User, Course\)\.join\(Teacher, Group\.teacher_id == Teacher\.id\)\.join\(User, Teacher\.user_id == User\.id\)\.join\(Course, Teacher\.course_id == Course\.id\)\.filter\(Group\.branch_id == current_user\.branch_id\)\.all\(\)",
    r"groups_q = db.session.query(Group, Teacher, User, Course).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).join(Course, Teacher.course_id == Course.id)\n    if current_user.role != 'superadmin':\n        groups_q = groups_q.filter(Group.branch_id == current_user.branch_id)\n    groups = groups_q.all()",
    text
)

# 5. Update Students query
text = re.sub(
    r"students = db\.session\.query\(Student, User, Group\)\.join\(User\)\.join\(Group\)\.filter\(User\.branch_id == current_user\.branch_id\)\.all\(\)",
    r"students_q = db.session.query(Student, User, Group).join(User).join(Group)\n    if current_user.role != 'superadmin':\n        students_q = students_q.filter(User.branch_id == current_user.branch_id)\n    students = students_q.all()",
    text
)

# 6. Update Tests query
text = re.sub(
    r"tests = db\.session\.query\(Test, Group, Teacher, User\)\.join\(Group, Test\.group_id == Group\.id\)\.join\(Teacher, Group\.teacher_id == Teacher\.id\)\.join\(User, Teacher\.user_id == User\.id\)\.filter\(Group\.branch_id == current_user\.branch_id\)\.all\(\)",
    r"tests_q = db.session.query(Test, Group, Teacher, User).join(Group, Test.group_id == Group.id).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id)\n    if current_user.role != 'superadmin':\n        tests_q = tests_q.filter(Group.branch_id == current_user.branch_id)\n    tests = tests_q.all()",
    text
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Superadmin bypass logic injected.")
