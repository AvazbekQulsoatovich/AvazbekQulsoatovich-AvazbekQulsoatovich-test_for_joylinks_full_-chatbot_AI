import sqlite3

def add_column():
    conn = sqlite3.connect('instance/joylinks_test.db')
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(test)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'description' not in columns:
            print("Adding 'description' column to 'test' table...")
            cursor.execute("ALTER TABLE test ADD COLUMN description TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("'description' column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
