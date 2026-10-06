from flask import Blueprint, jsonify
from backend.database import get_db_connection

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/faculty', methods=['GET'])
def get_faculty():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM faculty').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])