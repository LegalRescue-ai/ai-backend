# app/api/routes/category_routes.py
from flask import Blueprint, jsonify, request, current_app
from app.services.category.category_manager import CategoryManager

# Define Blueprint - fix __name__ syntax
category_bp = Blueprint("categories", __name__)

@category_bp.route("/", methods=["GET"])
def get_all_categories():
    """Retrieve all legal categories."""
    try:
        categories = CategoryManager.get_all_categories()
        return jsonify({
            "status": "success",
            "categories": categories,
            "total_categories": len(categories),
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving categories: {e}")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve categories.",
        }), 500