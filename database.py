import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT,
        email TEXT UNIQUE, mobile TEXT, dob TEXT, gender TEXT, course TEXT, year TEXT,
        division TEXT, address TEXT, status TEXT DEFAULT 'Active', attendance INTEGER DEFAULT 85)""")

    c.execute("""CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL DEFAULT '', subject TEXT DEFAULT '',
        description TEXT DEFAULT '', due_date TEXT DEFAULT '', status TEXT DEFAULT 'Pending')""")

    c.execute("""CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL DEFAULT '', subject TEXT DEFAULT '',
        exam_date TEXT DEFAULT '', start_time TEXT DEFAULT '', room TEXT DEFAULT '', max_marks INTEGER DEFAULT 100)""")

    c.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER DEFAULT 1, student_name TEXT DEFAULT '',
        subject TEXT NOT NULL DEFAULT '', exam TEXT DEFAULT 'Internal', marks REAL DEFAULT 0,
        max_marks REAL DEFAULT 100, total REAL DEFAULT 100, grade TEXT DEFAULT '',
        remarks TEXT DEFAULT '', result TEXT DEFAULT '',
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE)""")

    c.execute("""CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT DEFAULT 'General', category TEXT DEFAULT 'General',
        title TEXT NOT NULL DEFAULT '', details TEXT DEFAULT '', date TEXT DEFAULT '')""")

    c.execute("""CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT DEFAULT '', time TEXT DEFAULT '', subject TEXT DEFAULT '',
        room TEXT DEFAULT '', teacher TEXT DEFAULT '', monday TEXT DEFAULT '', tuesday TEXT DEFAULT '',
        wednesday TEXT DEFAULT '', thursday TEXT DEFAULT '', friday TEXT DEFAULT '')""")

    c.execute("""CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL DEFAULT '', email TEXT,
        department TEXT DEFAULT '', designation TEXT DEFAULT '')""")

    c.execute("""CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER DEFAULT 1, subject TEXT DEFAULT '',
        marks REAL DEFAULT 0, total REAL DEFAULT 100,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE)""")

    # Safe migrations for databases created by previous versions.
    definitions = {
        'assignments': {'title': "TEXT NOT NULL DEFAULT ''", 'subject': "TEXT DEFAULT ''", 'description': "TEXT DEFAULT ''", 'due_date': "TEXT DEFAULT ''", 'status': "TEXT DEFAULT 'Pending'"},
        'exams': {'title': "TEXT NOT NULL DEFAULT ''", 'subject': "TEXT DEFAULT ''", 'exam_date': "TEXT DEFAULT ''", 'start_time': "TEXT DEFAULT ''", 'room': "TEXT DEFAULT ''", 'max_marks': "INTEGER DEFAULT 100", 'exam_type': "TEXT DEFAULT 'Mid-Term'", 'date': "TEXT DEFAULT ''", 'time': "TEXT DEFAULT ''", 'total_marks': "INTEGER DEFAULT 100", 'passing_marks': "INTEGER DEFAULT 40"},
        'results': {'student_id': "INTEGER DEFAULT 1", 'student_name': "TEXT DEFAULT ''", 'subject': "TEXT NOT NULL DEFAULT ''", 'exam': "TEXT DEFAULT 'Internal'", 'marks': "REAL DEFAULT 0", 'max_marks': "REAL DEFAULT 100", 'total': "REAL DEFAULT 100", 'grade': "TEXT DEFAULT ''", 'remarks': "TEXT DEFAULT ''", 'result': "TEXT DEFAULT ''"},
        'notices': {'type': "TEXT DEFAULT 'General'", 'category': "TEXT DEFAULT 'General'", 'title': "TEXT NOT NULL DEFAULT ''", 'details': "TEXT DEFAULT ''", 'date': "TEXT DEFAULT ''"},
        'timetable': {'day': "TEXT DEFAULT ''", 'time': "TEXT DEFAULT ''", 'subject': "TEXT DEFAULT ''", 'room': "TEXT DEFAULT ''", 'teacher': "TEXT DEFAULT ''", 'monday': "TEXT DEFAULT ''", 'tuesday': "TEXT DEFAULT ''", 'wednesday': "TEXT DEFAULT ''", 'thursday': "TEXT DEFAULT ''", 'friday': "TEXT DEFAULT ''"},
    }
    for table, cols in definitions.items():
        existing = {r['name'] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}
        for col, definition in cols.items():
            if col not in existing:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {col} {definition}')

    # Backfill aliases without deleting existing records.
    conn.execute("UPDATE exams SET exam_type = COALESCE(NULLIF(exam_type,''), title)")
    conn.execute("UPDATE exams SET date = COALESCE(NULLIF(date,''), exam_date)")
    conn.execute("UPDATE exams SET time = COALESCE(NULLIF(time,''), start_time)")
    conn.execute("UPDATE exams SET total_marks = COALESCE(total_marks, max_marks, 100)")
    conn.execute("UPDATE notices SET category = COALESCE(NULLIF(category,''), type, 'General')")
    conn.execute("UPDATE results SET total = COALESCE(total, max_marks, 100)")

    conn.commit()
    conn.close()
    print('Database Initialized Successfully!')

if __name__ == '__main__':
    init_db()
