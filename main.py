import os
from flask import Flask, render_template
from flask_cors import CORS

from backend.database import init_db
from backend.routes.student import student_bp
from backend.routes.attendance import attendance_bp
from backend.routes.marks import marks_bp
from backend.routes.faculty import faculty_bp
from backend.routes.admin import admin_bp
from backend.routes.ai import ai_bp
from backend.routes.academic import academic_bp
from backend.auth import auth_bp

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app)

app.register_blueprint(student_bp, url_prefix="/v1")
app.register_blueprint(attendance_bp, url_prefix="/v1")
app.register_blueprint(ai_bp, url_prefix="/v1")
app.register_blueprint(marks_bp, url_prefix="/v1")
app.register_blueprint(faculty_bp, url_prefix="/v1")
app.register_blueprint(admin_bp, url_prefix="/v1")
app.register_blueprint(academic_bp, url_prefix="/v1")
app.register_blueprint(auth_bp, url_prefix="/v1/auth")

# Ensure all required SQLite tables/columns exist whenever the app starts.
# This is safe because init_db() uses CREATE TABLE IF NOT EXISTS and guarded
# migrations for older timetable/notices databases.
init_db()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
