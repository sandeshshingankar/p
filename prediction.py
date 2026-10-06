class PredictionService:
    @staticmethod
    def predict_performance(attendance_pct, internal_marks):
        """Predicts risk score and expected exam grade"""
        score = (attendance_pct * 0.4) + (internal_marks * 0.6)
        if score >= 80:
            return {"grade": "A+", "status": "Excellent", "risk": "Low"}
        elif score >= 60:
            return {"grade": "B", "status": "Good", "risk": "Moderate"}
        else:
            return {"grade": "C", "status": "Needs Improvement", "risk": "High"}