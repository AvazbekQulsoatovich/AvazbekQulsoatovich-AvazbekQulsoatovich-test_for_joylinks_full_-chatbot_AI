import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update admin_courses pagination
text = re.sub(
    r"(def admin_courses\(\):)\n\s*(courses = Course\.query\.all\(\) if current_user\.role == 'superadmin' else Course\.query\.filter_by\(branch_id=current_user\.branch_id\)\.all\(\))",
    r"\1\n    page = request.args.get('page', 1, type=int)\n    courses_q = Course.query if current_user.role == 'superadmin' else Course.query.filter_by(branch_id=current_user.branch_id)\n    pagination = courses_q.paginate(page=page, per_page=10, error_out=False)\n    courses = pagination.items",
    text
)
# Update admin_courses return
text = text.replace(
    "return render_template('admin/courses_modern.html', courses=courses)",
    "return render_template('admin/courses_modern.html', courses=courses, pagination=pagination)"
)

# 2. Update admin_teachers pagination
text = re.sub(
    r"(def admin_teachers\(\):)\n\s*(teachers_q = .*\n\s*if current_user\.role != 'superadmin':\n\s*teachers_q = .*\n\s*teachers = teachers_q\.all\(\))",
    r"\1\n    page = request.args.get('page', 1, type=int)\n    teachers_q = db.session.query(Teacher, User, Course).join(User).join(Course)\n    if current_user.role != 'superadmin':\n        teachers_q = teachers_q.filter(User.branch_id == current_user.branch_id)\n    pagination = teachers_q.paginate(page=page, per_page=10, error_out=False)\n    teachers = pagination.items",
    text
)
# Update admin_teachers return
text = text.replace(
    "return render_template('admin/teachers_modern.html', teachers=teachers)",
    "return render_template('admin/teachers_modern.html', teachers=teachers, pagination=pagination)"
)

# 3. Update admin_groups pagination
text = re.sub(
    r"(def admin_groups\(\):)\n\s*(groups_q = .*\n\s*if current_user\.role != 'superadmin':\n\s*groups_q = .*\n\s*groups = groups_q\.all\(\))",
    r"\1\n    page = request.args.get('page', 1, type=int)\n    groups_q = db.session.query(Group, Teacher, User, Course).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id).join(Course, Teacher.course_id == Course.id)\n    if current_user.role != 'superadmin':\n        groups_q = groups_q.filter(Group.branch_id == current_user.branch_id)\n    pagination = groups_q.paginate(page=page, per_page=10, error_out=False)\n    groups = pagination.items",
    text
)
# Update admin_groups return
text = text.replace(
    "return render_template('admin/groups_modern.html', groups=groups)",
    "return render_template('admin/groups_modern.html', groups=groups, pagination=pagination)"
)

# 4. Update admin_tests pagination
text = re.sub(
    r"(def admin_tests\(\):)\n\s*(tests_q = .*\n\s*if current_user\.role != 'superadmin':\n\s*tests_q = .*\n\s*tests = tests_q\.all\(\))",
    r"\1\n    page = request.args.get('page', 1, type=int)\n    tests_q = db.session.query(Test, Group, Teacher, User).join(Group, Test.group_id == Group.id).join(Teacher, Group.teacher_id == Teacher.id).join(User, Teacher.user_id == User.id)\n    if current_user.role != 'superadmin':\n        tests_q = tests_q.filter(Group.branch_id == current_user.branch_id)\n    pagination = tests_q.paginate(page=page, per_page=10, error_out=False)\n    tests = pagination.items",
    text
)
# Update admin_tests return (note current_time is also there)
text = text.replace(
    "return render_template('admin/tests_modern.html', tests=tests, current_time=current_time)",
    "return render_template('admin/tests_modern.html', tests=tests, current_time=current_time, pagination=pagination)"
)

# 5. Update admin_students pagination
text = re.sub(
    r"(def admin_students\(\):)\n\s*(from sqlalchemy\.orm import aliased\n\s*.*\n\s*.*\n\s*.*\n\s*students_data = .*\n\s*\.join\(.*\n\s*\.join\(.*\n\s*\.join\(.*\n\s*\.join\(.*\n\s*\.join\(.*\n\s*\.options\(.*\n\s*\.all\(\))",
    r"\1\n    from sqlalchemy.orm import aliased\n    page = request.args.get('page', 1, type=int)\n    student_user = aliased(User, name='student_user')\n    teacher_user = aliased(User, name='teacher_user')\n    students_q = db.session.query(Student, student_user, Group, Teacher, teacher_user, Course)\\\n        .join(student_user, Student.user_id == student_user.id)\\\n        .join(Group, Student.group_id == Group.id)\\\n        .join(Teacher, Group.teacher_id == Teacher.id)\\\n        .join(teacher_user, Teacher.user_id == teacher_user.id)\\\n        .join(Course, Teacher.course_id == Course.id)\\\n        .options(db.joinedload(Student.results))\n    if current_user.role != 'superadmin':\n        students_q = students_q.filter(student_user.branch_id == current_user.branch_id)\n    pagination = students_q.paginate(page=page, per_page=10, error_out=False)\n    students_data = pagination.items",
    text
)
# Update admin_students return
text = text.replace(
    "return render_template('admin/students_modern.html', students=students)",
    "return render_template('admin/students_modern.html', students=students, pagination=pagination)"
)

# 6. Update admin_results pagination
text = re.sub(
    r"(def admin_results\(\):)\n\s*(results = db\.session\.query\(TestResult, Student, User, Group, Test\)\\\n\s*\.join\(Student, TestResult\.student_id == Student\.id\)\\\n\s*\.join\(User, Student\.user_id == User\.id\)\\\n\s*\.join\(Group, Student\.group_id == Group\.id\)\\\n\s*\.join\(Test, TestResult\.test_id == Test\.id\)\\\n\s*\.all\(\))",
    r"\1\n    page = request.args.get('page', 1, type=int)\n    results_q = db.session.query(TestResult, Student, User, Group, Test)\\\n        .join(Student, TestResult.student_id == Student.id)\\\n        .join(User, Student.user_id == User.id)\\\n        .join(Group, Student.group_id == Group.id)\\\n        .join(Test, TestResult.test_id == Test.id)\n    if current_user.role != 'superadmin':\n        results_q = results_q.filter(Group.branch_id == current_user.branch_id)\n    pagination = results_q.paginate(page=page, per_page=10, error_out=False)\n    results = pagination.items",
    text
)
# Update admin_results return
text = text.replace(
    "return render_template('admin/results_modern.html', results=results)",
    "return render_template('admin/results_modern.html', results=results, pagination=pagination)"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Pagination logic injected into app.py.")
