# app/api/routes/general_routes.py
from flask import Blueprint, jsonify


# Define Blueprint - fix __name__ syntax
general_bp = Blueprint("general", __name__)

@general_bp.route("/health", methods=["GET"])
def health_check():
    """Check system health status."""
    