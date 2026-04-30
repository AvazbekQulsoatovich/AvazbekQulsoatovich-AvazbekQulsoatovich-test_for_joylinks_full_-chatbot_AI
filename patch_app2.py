import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# adding branch_id to User creations in admin_ routes
content = re.sub(
    r"role='teacher',\s*full_name=full_name\s*\)",
    r"role='teacher',\n            full_name=full_name,\n            branch_id=current_user.branch_id\n        )",
    content
)

content = re.sub(
    r"role='student',\s*full_name=full_name\s*\)",
    r"role='student',\n            full_name=full_name,\n            branch_id=current_user.branch_id\n        )",
    content
)

# get_or_404 constraints
content = re.sub(
    r"Student\.query\.get_or_404\((.*?)\)",
    r"Student.query.join(User).filter(User.branch_id == current_user.branch_id, Student.id == \1).first_or_404()",
    content
)
content = re.sub(
    r"Teacher\.query\.get_or_404\((.*?)\)",
    r"Teacher.query.join(User).filter(User.branch_id == current_user.branch_id, Teacher.id == \1).first_or_404()",
    content
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch 2 done.")
