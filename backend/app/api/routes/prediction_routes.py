# app/api/routes/prediction_routes.py
from flask import Blueprint, request, jsonify
from app.services.prediction.category_predictor import CategoryPredictor

# Define Blueprint - fix __name__ syntax
prediction_bp = Blueprint("predictions", __name__)

@prediction_bp.route("/predict", methods=["POST"])
def predict_category():
    """Predict the category of a legal case based on input text."""
    try:
        data = request.get_json()
        prediction = CategoryPredictor.predict_category(data["text"])
        return jsonify({"status": "success", "prediction": prediction}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500