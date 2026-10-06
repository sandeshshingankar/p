from flask import Blueprint, jsonify, request
from backend.services.chatbot import ChatbotService
from backend.services.prediction import PredictionService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '')
    response_text = ChatbotService.get_response(message)
    return jsonify({"mode": "study", "response": response_text})

@ai_bp.route('/ai/predict', methods=['GET'])
def predict():
    result = PredictionService.predict_performance(attendance_pct=92, internal_marks=85)
    return jsonify(result)