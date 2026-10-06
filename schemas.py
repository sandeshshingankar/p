def validate_student_data(data):
    """Validation helper for student registration"""
    required_fields = ['first_name', 'email', 'course']
    for field in required_fields:
        if not data.get(field):
            return False, f"Field '{field}' is required."
    return True, "Valid"

def serialize_student(student_dict):
    """Formats student dict for clean JSON responses"""
    if not student_dict:
        return {}
    full_name = f"{student_dict.get('first_name', '')} {student_dict.get('last_name', '')}".strip()
    return {
        "id": student_dict.get("id"),
        "name": full_name or student_dict.get("first_name"),
        "email": student_dict.get("email"),
        "course": student_dict.get("course"),
        "status": student_dict.get("status", "Active"),
        "attendance": student_dict.get("attendance", 0)
    }