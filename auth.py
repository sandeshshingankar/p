from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')

    # Demo Authentication Logic
    if email == "student@college.com" and password == "123456":
        return jsonify({"status": "success", "message": "Login Successful", "token": "demo-jwt-token-2026"})
    return jsonify({"status": "error", "message": "Invalid Credentials"}), 401