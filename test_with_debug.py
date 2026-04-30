import requests
import time

# Test with debug monitoring
session = requests.Session()

print("=== DEBUG MONITORING TEST ===")
print()

# Login as asilbek
login_data = {
    'username': 'assi',
    'password': 'assi123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Login successful!")
    
    # Wait a moment for logs to appear
    time.sleep(1)
    
    # Direct submit
    submit_data = {
        'question_2': 'B'
    }
    
    print("Submitting test...")
    submit_response = session.post('http://127.0.0.1:5000/student/test/2/submit', data=submit_data)
    
    print(f"Submit status: {submit_response.status_code}")
    
    # Wait for debug logs
    time.sleep(2)
    
    # Check if result was saved
    from app import app, db, TestResult, Student, User
    
    with app.app_context():
        asilbek_user = User.query.filter_by(username='assi').first()
        asilbek_student = Student.query.filter_by(user_id=asilbek_user.id).first()
        
        result = TestResult.query.filter_by(student_id=asilbek_student.id, test_id=2).first()
        
        if result:
            print(f"✅ Natija saqlandi!")
            print(f"   Ball: {result.score}/{result.total_questions}")
            print(f"   Foiz: {result.percentage}%")
        else:
            print("❌ Natija saqlanmadi!")
else:
    print("❌ Login xato")

print("\nFlask loglarini tekshiring (command_status orqali)")
