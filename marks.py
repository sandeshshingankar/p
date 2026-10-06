from flask import Blueprint, jsonify
from backend.database import get_db_connection

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['GET'])
def get_marks():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM marks WHERE student_id = 1').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])