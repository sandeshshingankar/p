from flask import Blueprint, jsonify
from backend.database import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    conn = get_db_connection()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_faculty = conn.execute('SELECT COUNT(*) FROM faculty').fetchone()[0]
    conn.close()
    return jsonify({
        "total_students": total_students,
        "total_faculty": total_faculty,
        "system_status": "Optimal"
    })