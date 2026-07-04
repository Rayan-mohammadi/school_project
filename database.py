import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'school.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جدول دانش‌آموزان
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            student_code TEXT NOT NULL UNIQUE,
            father_name TEXT NOT NULL,
            grade TEXT NOT NULL,
            major TEXT NOT NULL,
            photo_path TEXT
        )
    ''')
    
    # جدول نمرات (با ستون score)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            lesson TEXT NOT NULL,
            score REAL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            UNIQUE(student_id, lesson)
        )
    ''')
    
    conn.commit()
    conn.close()

# برای مواقعی که جدول قبلاً ساخته شده ولی ستون score رو نداره
def upgrade_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # بررسی وجود ستون score
    cursor.execute("PRAGMA table_info(grades)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'score' not in columns:
        print("Adding score column to grades table...")
        # ساخت جدول جدید با ستون score
        cursor.execute('''
            CREATE TABLE grades_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                lesson TEXT NOT NULL,
                score REAL,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                UNIQUE(student_id, lesson)
            )
        ''')
        # کپی داده‌های قدیمی (اگه وجود داشته باشن)
        cursor.execute('''
            INSERT INTO grades_new (id, student_id, lesson)
            SELECT id, student_id, lesson FROM grades
        ''')
        cursor.execute('DROP TABLE grades')
        cursor.execute('ALTER TABLE grades_new RENAME TO grades')
        conn.commit()
        print("Done.")
    
    conn.close()

# اجرا
create_tables()
upgrade_database()