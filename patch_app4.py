import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace User model constraint
content = re.sub(
    r'class User\(UserMixin, db\.Model\):\n\s*id = db\.Column\(db\.Integer, primary_key=True\)\n\s*username = db\.Column\(db\.String\(80\), unique=True, nullable=False\)',
    r"class User(UserMixin, db.Model):\n    __table_args__ = (\n        db.UniqueConstraint('branch_id', 'username', name='uix_branch_username'),\n    )\n    id = db.Column(db.Integer, primary_key=True)\n    username = db.Column(db.String(80), nullable=False)",
    content
)

# Replace uniqueness checks in add_student and add_teacher
content = re.sub(
    r'if User\.query\.filter_by\(username=username\)\.first\(\)',
    r'if User.query.filter_by(username=username, branch_id=current_user.branch_id).first()',
    content
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching constraints done.")
