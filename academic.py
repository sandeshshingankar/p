from flask import Blueprint, jsonify, request
from backend.database import get_db_connection
import sqlite3

academic_bp = Blueprint("academic", __name__)

# The desktop Tkinter frontend uses these legacy field names.  The backend
# accepts both the legacy names and the canonical database names so the UI
# and database stay compatible.
RESOURCE_CONFIG = {
    "assignments": {
        "table": "assignments",
        "required": ["title"],
        "fields": ["title", "subject", "description", "due_date", "status"],
    },
    "exams": {
        "table": "exams",
        "required": ["subject"],
        "fields": ["title", "subject", "exam_date", "start_time", "room", "max_marks",
                   "exam_type", "date", "time", "total_marks", "passing_marks"],
    },
    "results": {
        "table": "results",
        "required": ["subject"],
        "fields": ["student_id", "student_name", "subject", "exam", "marks", "max_marks",
                   "total", "grade", "remarks", "result"],
    },
    "notices": {
        "table": "notices",
        "required": ["title"],
        "fields": ["type", "category", "title", "details", "date"],
    },
    "timetable": {
        "table": "timetable",
        "required": ["time"],
        "fields": ["day", "time", "subject", "room", "teacher",
                   "monday", "tuesday", "wednesday", "thursday", "friday"],
    },
}


def clean_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def get_config(resource):
    return RESOURCE_CONFIG.get(resource)


def ensure_compat_columns(conn):
    """Add columns used by the existing desktop UI to older databases."""
    definitions = {
        "assignments": {
            "title": "TEXT NOT NULL DEFAULT ''",
            "subject": "TEXT DEFAULT ''",
            "description": "TEXT DEFAULT ''",
            "due_date": "TEXT DEFAULT ''",
            "status": "TEXT DEFAULT 'Pending'",
        },
        "exams": {
            "title": "TEXT NOT NULL DEFAULT ''",
            "subject": "TEXT DEFAULT ''",
            "exam_date": "TEXT DEFAULT ''",
            "start_time": "TEXT DEFAULT ''",
            "room": "TEXT DEFAULT ''",
            "max_marks": "INTEGER DEFAULT 100",
            "exam_type": "TEXT DEFAULT 'Mid-Term'",
            "date": "TEXT DEFAULT ''",
            "time": "TEXT DEFAULT ''",
            "total_marks": "INTEGER DEFAULT 100",
            "passing_marks": "INTEGER DEFAULT 40",
        },
        "results": {
            "student_id": "INTEGER DEFAULT 1",
            "student_name": "TEXT DEFAULT ''",
            "subject": "TEXT NOT NULL DEFAULT ''",
            "exam": "TEXT DEFAULT 'Internal'",
            "marks": "REAL DEFAULT 0",
            "max_marks": "REAL DEFAULT 100",
            "total": "REAL DEFAULT 100",
            "grade": "TEXT DEFAULT ''",
            "remarks": "TEXT DEFAULT ''",
            "result": "TEXT DEFAULT ''",
        },
        "notices": {
            "type": "TEXT DEFAULT 'General'",
            "category": "TEXT DEFAULT 'General'",
            "title": "TEXT NOT NULL DEFAULT ''",
            "details": "TEXT DEFAULT ''",
            "date": "TEXT DEFAULT ''",
        },
        "timetable": {
            "day": "TEXT DEFAULT ''",
            "time": "TEXT DEFAULT ''",
            "subject": "TEXT DEFAULT ''",
            "room": "TEXT DEFAULT ''",
            "teacher": "TEXT DEFAULT ''",
            "monday": "TEXT DEFAULT ''",
            "tuesday": "TEXT DEFAULT ''",
            "wednesday": "TEXT DEFAULT ''",
            "thursday": "TEXT DEFAULT ''",
            "friday": "TEXT DEFAULT ''",
        },
    }
    for table, cols in definitions.items():
        existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for col, definition in cols.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")

    # Keep canonical exam fields synchronized with the legacy UI fields.
    conn.execute("UPDATE exams SET title = CASE WHEN title IS NULL OR title='' THEN exam_type ELSE title END")
    conn.execute("UPDATE exams SET exam_date = CASE WHEN exam_date IS NULL OR exam_date='' THEN date ELSE exam_date END")
    conn.execute("UPDATE exams SET start_time = CASE WHEN start_time IS NULL OR start_time='' THEN time ELSE start_time END")
    conn.execute("UPDATE exams SET max_marks = CASE WHEN max_marks IS NULL THEN total_marks ELSE max_marks END")
    conn.execute("UPDATE exams SET exam_type = CASE WHEN exam_type IS NULL OR exam_type='' THEN title ELSE exam_type END")
    conn.execute("UPDATE exams SET date = CASE WHEN date IS NULL OR date='' THEN exam_date ELSE date END")
    conn.execute("UPDATE exams SET time = CASE WHEN time IS NULL OR time='' THEN start_time ELSE time END")
    conn.execute("UPDATE exams SET total_marks = CASE WHEN total_marks IS NULL THEN max_marks ELSE total_marks END")


def row_for_frontend(resource, row):
    d = dict(row)
    if resource == "exams":
        d["exam_type"] = d.get("exam_type") or d.get("title", "")
        d["date"] = d.get("date") or d.get("exam_date", "")
        d["time"] = d.get("time") or d.get("start_time", "")
        d["total_marks"] = d.get("total_marks") if d.get("total_marks") is not None else d.get("max_marks", 100)
        d["passing_marks"] = d.get("passing_marks", 40)
    elif resource == "results":
        d["total"] = d.get("total") if d.get("total") is not None else d.get("max_marks", 100)
        if not d.get("student_name") and d.get("student_id"):
            conn = get_db_connection()
            student = conn.execute(
                "SELECT first_name, last_name FROM students WHERE id = ?",
                (d["student_id"],),
            ).fetchone()
            conn.close()
            if student:
                d["student_name"] = f"{student['first_name']} {student['last_name'] or ''}".strip()
        if not d.get("result"):
            try:
                d["result"] = "Pass" if float(d.get("marks", 0)) >= float(d.get("total", 100)) * 0.4 else "Fail"
            except Exception:
                d["result"] = ""
    elif resource == "notices":
        d["category"] = d.get("category") or d.get("type", "General")
    return d


@academic_bp.get("/health")
def health():
    return jsonify({"status": "ok", "backend": "online"})


@academic_bp.get("/<resource>")
def list_resource(resource):
    cfg = get_config(resource)
    if not cfg:
        return jsonify({"error": "Unknown resource"}), 404
    conn = get_db_connection()
    ensure_compat_columns(conn)
    rows = conn.execute(f"SELECT * FROM {cfg['table']} ORDER BY id DESC").fetchall()
    conn.commit()
    conn.close()
    return jsonify([row_for_frontend(resource, row) for row in rows])


@academic_bp.post("/<resource>")
def create_resource(resource):
    cfg = get_config(resource)
    if not cfg:
        return jsonify({"error": "Unknown resource"}), 404

    data = request.get_json(silent=True) or {}
    missing = [f for f in cfg["required"] if not clean_value(data.get(f))]
    if missing:
        return jsonify({"error": f"Required field(s): {', '.join(missing)}"}), 400

    conn = get_db_connection()
    ensure_compat_columns(conn)

    if resource == "exams":
        exam_type = clean_value(data.get("exam_type") or data.get("title") or "Mid-Term")
        date = clean_value(data.get("date") or data.get("exam_date") or "")
        time = clean_value(data.get("time") or data.get("start_time") or "")
        total = int(float(data.get("total_marks") or data.get("max_marks") or 100))
        passing = int(float(data.get("passing_marks") or 40))
        values = {
            "title": clean_value(data.get("title") or exam_type),
            "subject": clean_value(data.get("subject")),
            "exam_date": date,
            "start_time": time,
            "room": clean_value(data.get("room") or ""),
            "max_marks": total,
            "exam_type": exam_type,
            "date": date,
            "time": time,
            "total_marks": total,
            "passing_marks": passing,
        }
    elif resource == "results":
        try:
            student_id = int(data.get("student_id") or 1)
            marks = float(data.get("marks") or 0)
            total = float(data.get("total") or data.get("max_marks") or 100)
        except (TypeError, ValueError):
            conn.close()
            return jsonify({"error": "Student ID, Marks and Total Marks must be valid numbers."}), 400
        result = clean_value(data.get("result")) or ("Pass" if marks >= total * 0.4 else "Fail")
        values = {
            "student_id": student_id,
            "student_name": clean_value(data.get("student_name") or ""),
            "subject": clean_value(data.get("subject")),
            "exam": clean_value(data.get("exam") or "Internal"),
            "marks": marks,
            "max_marks": total,
            "total": total,
            "grade": clean_value(data.get("grade") or ""),
            "remarks": clean_value(data.get("remarks") or ""),
            "result": result,
        }
    elif resource == "notices":
        category = clean_value(data.get("category") or data.get("type") or "General")
        values = {
            "type": category,
            "category": category,
            "title": clean_value(data.get("title")),
            "details": clean_value(data.get("details") or ""),
            "date": clean_value(data.get("date") or ""),
        }
    elif resource == "timetable":
        # The existing UI stores one weekly row: Time + Monday-Friday cells.
        # Keep that shape in SQLite so Add/Edit/Delete match the visible table.
        values = {
            "day": "",
            "time": clean_value(data.get("time") or ""),
            "subject": clean_value(data.get("subject") or ""),
            "room": clean_value(data.get("room") or ""),
            "teacher": clean_value(data.get("teacher") or ""),
            "monday": clean_value(data.get("monday") or ""),
            "tuesday": clean_value(data.get("tuesday") or ""),
            "wednesday": clean_value(data.get("wednesday") or ""),
            "thursday": clean_value(data.get("thursday") or ""),
            "friday": clean_value(data.get("friday") or ""),
        }
    else:
        values = {field: clean_value(data.get(field)) for field in cfg["fields"] if field in data and field in {r["name"] for r in conn.execute(f"PRAGMA table_info({cfg['table']})").fetchall()}}

    if not values:
        conn.close()
        return jsonify({"error": "No valid fields supplied."}), 400

    columns = ", ".join(values.keys())
    placeholders = ", ".join(["?"] * len(values))
    try:
        cur = conn.execute(
            f"INSERT INTO {cfg['table']} ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )
        conn.commit()
        row = conn.execute(f"SELECT * FROM {cfg['table']} WHERE id = ?", (cur.lastrowid,)).fetchone()
        conn.close()
        return jsonify(row_for_frontend(resource, row)), 201
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500


@academic_bp.put("/<resource>/<int:item_id>")
def update_resource(resource, item_id):
    cfg = get_config(resource)
    if not cfg:
        return jsonify({"error": "Unknown resource"}), 404
    data = request.get_json(silent=True) or {}
    conn = get_db_connection()
    ensure_compat_columns(conn)

    if resource == "exams":
        values = {
            "title": clean_value(data.get("title") or data.get("exam_type")),
            "subject": clean_value(data.get("subject")),
            "exam_date": clean_value(data.get("exam_date") or data.get("date")),
            "start_time": clean_value(data.get("start_time") or data.get("time")),
            "room": clean_value(data.get("room")),
            "max_marks": int(float(data.get("max_marks") or data.get("total_marks") or 100)),
            "exam_type": clean_value(data.get("exam_type") or data.get("title")),
            "date": clean_value(data.get("date") or data.get("exam_date")),
            "time": clean_value(data.get("time") or data.get("start_time")),
            "total_marks": int(float(data.get("total_marks") or data.get("max_marks") or 100)),
            "passing_marks": int(float(data.get("passing_marks") or 40)),
        }
    elif resource == "results":
        values = {}
        if "student_id" in data:
            values["student_id"] = int(data["student_id"] or 1)
        if "student_name" in data: values["student_name"] = clean_value(data["student_name"])
        if "subject" in data: values["subject"] = clean_value(data["subject"])
        if "marks" in data: values["marks"] = float(data["marks"] or 0)
        if "total" in data or "max_marks" in data:
            values["total"] = float(data.get("total") or data.get("max_marks") or 100)
            values["max_marks"] = values["total"]
        if "grade" in data: values["grade"] = clean_value(data["grade"])
        if "result" in data: values["result"] = clean_value(data["result"])
        if "exam" in data: values["exam"] = clean_value(data["exam"])
        if "remarks" in data: values["remarks"] = clean_value(data["remarks"])
    elif resource == "notices":
        category = clean_value(data.get("category") or data.get("type") or "General")
        values = {
            "type": category,
            "category": category,
            "title": clean_value(data.get("title")),
            "details": clean_value(data.get("details")),
            "date": clean_value(data.get("date")),
        }
    elif resource == "timetable":
        values = {k: clean_value(data.get(k)) for k in
                  ["time", "subject", "room", "teacher", "monday", "tuesday", "wednesday", "thursday", "friday"]
                  if k in data}
    else:
        table_cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({cfg['table']})").fetchall()}
        values = {field: clean_value(data.get(field)) for field in cfg["fields"] if field in data and field in table_cols}

    values = {k: v for k, v in values.items() if v is not None}
    if not values:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400

    try:
        set_clause = ", ".join([f"{field} = ?" for field in values])
        cur = conn.execute(
            f"UPDATE {cfg['table']} SET {set_clause} WHERE id = ?",
            tuple(values.values()) + (item_id,),
        )
        if cur.rowcount == 0:
            conn.rollback()
            conn.close()
            return jsonify({"error": "Record not found"}), 404
        conn.commit()
        row = conn.execute(f"SELECT * FROM {cfg['table']} WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        return jsonify(row_for_frontend(resource, row))
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 400


@academic_bp.delete("/<resource>/<int:item_id>")
def delete_resource(resource, item_id):
    cfg = get_config(resource)
    if not cfg:
        return jsonify({"error": "Unknown resource"}), 404
    conn = get_db_connection()
    ensure_compat_columns(conn)
    cur = conn.execute(f"DELETE FROM {cfg['table']} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"status": "success", "id": item_id})
