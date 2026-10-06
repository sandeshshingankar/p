from backend.database import get_db_connection

class StudentModel:
    @staticmethod
    def get_by_id(student_id=1):
        conn = get_db_connection()
        student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        return dict(student) if student else None

    @staticmethod
    def create(data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (first_name, last_name, email, mobile, dob, gender, course, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data.get('first_name'), data.get('last_name'), data.get('email'),
              data.get('mobile'), data.get('dob'), data.get('gender'),
              data.get('course'), data.get('address')))
        conn.commit()
        conn.close()
        return True