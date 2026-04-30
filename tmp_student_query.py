from app import app, Student, User, Group, Branch, TestResult

with app.app_context():
    s = Student.query.get(8)
    if not s:
        print('NOT_FOUND')
    else:
        u = User.query.get(s.user_id)
        g = Group.query.get(s.group_id)
        b = Branch.query.get(u.branch_id) if u and u.branch_id else None
        results = TestResult.query.filter_by(student_id=s.id).order_by(TestResult.submitted_at.desc()).all()
        print('STUDENT_ID', s.id)
        print('USERNAME', u.username if u else 'None')
        print('FULL_NAME', u.full_name if u else 'None')
        print('ROLE', u.role if u else 'None')
        print('BRANCH', b.name if b else 'None')
        print('GROUP', g.name if g else 'None')
        print('RESULTS_COUNT', len(results))
        for r in results[:5]:
            t = r.test
            print('RESULT', r.id, 'TEST', t.title if t else 'None', 'PERC', r.percentage, 'SCORE', r.score, '/', r.total_questions, 'DATE', r.submitted_at)
