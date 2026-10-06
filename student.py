from flask import Blueprint, jsonify, request
import sqlite3
from backend.database import get_db_connection

student_bp = Blueprint('student', __name__)

@student_bp.route('/student', methods=['GET'])
@student_bp.route('/student/profile', methods=['GET'])
def get_student_profile():
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE first_name != '' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if student:
        full_name = f"{student['first_name']} {student['last_name'] or ''}".strip()
        return jsonify({
            "id": student["id"],
            "name": full_name,
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "email": student["email"],
            "course": student["course"],
            "status": student["status"],
            "attendance": student["attendance"]
        })
    return jsonify({"error": "Student not found"}), 404

@student_bp.route('/students/all', methods=['GET'])
def get_all_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@student_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        dob = data.get('dob', '').strip()
        gender = data.get('gender', 'Not Specified').strip()
        course = data.get('course', '').strip()
        year = data.get('year', '').strip()
        division = data.get('division', '').strip()
        address = data.get('address', '').strip()

        if not first_name or not email:
            return jsonify({"error": "First Name and Email cannot be empty!"}), 400

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO students
            (first_name, last_name, email, mobile, dob, gender, course, year, division, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, mobile, dob, gender, course, year, division, address))
        conn.commit()
        conn.close()

        return jsonify({"message": "Registration Successful", "status": "success"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@student_bp.route('/student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json(silent=True) or {}
        allowed = ["first_name", "last_name", "email", "mobile", "course", "year", "division"]
        values = {k: data.get(k) for k in allowed if k in data}
        values = {k: (v.strip() if isinstance(v, str) else v) for k, v in values.items()}
        if not values:
            return jsonify({"error": "No fields to update"}), 400
        if not values.get("first_name"):
            return jsonify({"error": "First Name cannot be empty"}), 400
        if not values.get("email"):
            return jsonify({"error": "Email cannot be empty"}), 400

        set_clause = ", ".join(f"{k} = ?" for k in values)
        conn = get_db_connection()
        cur = conn.execute(
            f"UPDATE students SET {set_clause} WHERE id = ?",
            tuple(values.values()) + (student_id,),
        )
        if cur.rowcount == 0:
            conn.rollback()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        conn.commit()
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        return jsonify(dict(row))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@student_bp.route('/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        conn = get_db_connection()
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        if cur.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        return jsonify({"message": "Student deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Academic resource APIs (/assignments, /exams, /results, /notices, /timetable)
# are defined only in backend/routes/academic.py. Keeping one owner per URL
# prevents Flask endpoint collisions and keeps CRUD/database behavior consistent.
