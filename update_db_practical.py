import sqlite3
import os

db_path = os.path.join('instance', 'joylinks_test.db')

def update_db():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add columns to 'test' table
        print("Adding columns to 'test' table...")
        cursor.execute("ALTER TABLE test ADD COLUMN has_practical BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE test ADD COLUMN practical_file VARCHAR(255)")
        cursor.execute("ALTER TABLE test ADD COLUMN practical_description TEXT")
    except sqlite3.OperationalError as e:
        print(f"Note: {e}")

    try:
        # Add column to 'test_result' table
        print("Adding columns to 'test_result' table...")
        cursor.execute("ALTER TABLE test_result ADD COLUMN practical_submission VARCHAR(255)")
    except sqlite3.OperationalError as e:
        print(f"Note: {e}")

    try:
        # Add grading columns to 'test_result' table
        print("Adding grading columns to 'test_result' table...")
        cursor.execute("ALTER TABLE test_result ADD COLUMN practical_score INTEGER")
        cursor.execute("ALTER TABLE test_result ADD COLUMN practical_feedback TEXT")
    except sqlite3.OperationalError as e:
        print(f"Note: {e}")

    conn.commit()
    conn.close()
    print("Database update completed.")

if __name__ == "__main__":
    update_db()
