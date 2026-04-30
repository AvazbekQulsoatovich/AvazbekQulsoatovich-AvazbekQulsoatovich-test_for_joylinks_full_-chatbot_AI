from app import app, db, Student, User

# Create a minimal student dashboard route to test
@app.route('/test/student/dashboard')
def test_student_dashboard():
    try:
        student = db.session.query(Student).filter_by(user_id=1).first()  # Hardcoded user ID for testing
        if student:
            return f"Student found: {student.user.username}, Group: {student.group.name if student.group else 'None'}"
        else:
            return "Student not found"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    with app.test_client() as client:
        response = client.get('/test/student/dashboard')
        print(f"Test response: {response.status_code}")
        print(f"Response data: {response.data.decode()}")
