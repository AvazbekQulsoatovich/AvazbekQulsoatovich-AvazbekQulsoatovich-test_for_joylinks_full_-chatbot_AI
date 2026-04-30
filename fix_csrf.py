import os
import re

templates_dir = 'templates'
files_to_fix = [
    'admin/add_course.html',
    'admin/add_course_modern.html',
    'admin/add_teacher.html',
    'admin/add_teacher_modern.html',
    'admin/courses.html',
    'admin/edit_course.html',
    'admin/edit_course_modern.html',
    'admin/edit_group_modern.html',
    'admin/edit_teacher.html',
    'admin/edit_teacher_modern.html',
    'admin/groups_modern.html',
    'admin/teachers.html',
    'admin/tests_modern.html',
    'student/take_test.html',
    'teacher/add_group.html',
    'teacher/add_group_modern.html',
    'teacher/add_student.html',
    'teacher/add_student_modern.html',
    'teacher/add_test.html',
    'teacher/add_test_modern.html',
    'teacher/edit_group.html',
    'teacher/edit_student.html',
    'teacher/edit_test.html',
    'teacher/edit_test_modern.html',
    'teacher/groups.html',
    'teacher/students.html',
    'teacher/students_modern.html',
    'teacher/tests.html',
    'teacher/tests_modern.html',
    'login.html'
]

csrf_input = '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'

for rel_path in files_to_fix:
    path = os.path.join(templates_dir, rel_path)
    if not os.path.exists(path):
        print(f"Skipping {path} - not found")
        continue
    
    with open(path, 'r') as f:
        content = f.read()
    
    if 'csrf_token' in content:
        print(f"Skipping {path} - already has csrf_token")
        continue

    # Find the <form method="POST"> or <form ... method="post" ...>
    new_content = re.sub(r'(<form[^>]*method=["\']POST["\'][^>]*>)', r'\1\n                ' + csrf_input, content, flags=re.IGNORECASE)
    
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f"Fixed {path}")
    else:
        print(f"Could not find POST form in {path}")
