import sqlite3
import os

db_path = 'instance/joylinks_test.db'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(test)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_active' not in columns:
        print("Adding 'is_active' column to 'test' table...")
        cursor.execute("ALTER TABLE test ADD COLUMN is_active BOOLEAN DEFAULT 1")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column 'is_active' already exists.")
        
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
