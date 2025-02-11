from flask import Blueprint
from .case import case_bp
from .category_routes import category_bp
from .form_routes import form_bp
from .general_routes import general_bp
from .prediction_routes import prediction_bp

# Create a main api blueprint
api_bp = Blueprint('api', __name__)

# Register all route blueprints as sub-blueprints
api_bp.register_blueprint(case_bp, url_prefix='/case')
api_bp.register_blueprint(category_bp, url_prefix='/categories')
api_bp.register_blueprint(form_bp, url_prefix='/forms')
api_bp.register_blueprint(general_bp, url_prefix='/general')
api_bp.register_blueprint(prediction_bp, url_prefix='/predictions')

# Import all routes to ensure they are registered
from . import case, category_routes, form_routes, general_routes, prediction_routes