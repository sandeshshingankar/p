from flask import Blueprint, jsonify
from backend.models import StudentModel

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    student = StudentModel.get_by_id(1)
    overall = student.get('attendance', 85) if student else 85
    return jsonify({
        "overall": overall,
        "subjects": [
            {"name": "Data Structures", "percentage": 88},
            {"name": "Computer Networks", "percentage": 76},
            {"name": "Database Management", "percentage": 90}
        ]
    })