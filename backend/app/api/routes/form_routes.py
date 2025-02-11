# app/api/routes/form_routes.py
from flask import Blueprint, request, jsonify
from app.services.form.form_generator import FormGenerator

# Define Blueprint - fix __name__ syntax
form_bp = Blueprint("forms", __name__)

@form_bp.route("/generate", methods=["POST"])
def generate_form():
    """Generate a legal form based on input data."""
    try:
        data = request.get_json()
        form_data = FormGenerator.generate_form(data)
        return jsonify({"status": "success", "form": form_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500