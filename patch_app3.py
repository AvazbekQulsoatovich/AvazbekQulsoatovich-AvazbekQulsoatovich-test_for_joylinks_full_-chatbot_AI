import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# patch admin_export_students
content = re.sub(
    r'\.join\(Course, Teacher\.course_id == Course\.id\)\\\n\s*\.all\(\)',
    r'.join(Course, Teacher.course_id == Course.id)\\\n        .filter(Group.branch_id == current_user.branch_id)\\\n        .all()',
    content
)

# patch admin_export_results
content = re.sub(
    r'\.join\(Test, TestResult\.test_id == Test\.id\)\\\n\s*\.order_by',
    r'.join(Test, TestResult.test_id == Test.id)\\\n        .filter(Group.branch_id == current_user.branch_id)\\\n        .order_by',
    content
)

# wait there could be multiple .join(Test...
# Let's use simple string replacements for the exact statements in admin_export_results and admin_analytics
content = content.replace(
    ".join(Test, TestResult.test_id == Test.id)\\\n        .order_by(TestResult.submitted_at.desc())\\\n        .all()",
    ".join(Test, TestResult.test_id == Test.id)\\\n        .filter(Group.branch_id == current_user.branch_id)\\\n        .order_by(TestResult.submitted_at.desc())\\\n        .all()"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch 3 done.")
