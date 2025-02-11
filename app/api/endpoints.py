from flask import Blueprint, jsonify, current_app
from app.services.category.category_manager import CategoryManager
from app.services.health_check import HealthCheckService

# Create a general endpoints blueprint
general_bp = Blueprint('general', __name__)

class GeneralEndpoints:
    @staticmethod
    @general_bp.route('/health', methods=['GET'])
    def health_check():
        """
        Provide system health check endpoint
        
        Returns:
        JSON response with system health status
        """
        try:
            # Perform health checks
            health_check_service = HealthCheckService()
            health_status = health_check_service.perform_checks()

            return jsonify({
                "status": "success",
                "service": "Legal Case Management System",
                "health": health_status
            }), 200

        except Exception as e:
            current_app.logger.error(f"Health check error: {e}")
            return jsonify({
                "status": "error",
                "message": "Health check failed"
            }), 500

    @staticmethod
    @general_bp.route('/system-info', methods=['GET'])
    def get_system_info():
        """
        Retrieve system and configuration information
        
        Returns:
        JSON response with system details
        """
        try:
            # Gather system information
            system_info = {
                "service_name": "Legal Case Management System",
                "version": "1.0.0",
                "environment": current_app.config.get('ENV', 'Unknown'),
                "debug_mode": current_app.config.get('DEBUG', False),
                "available_categories": CategoryManager.get_all_categories(),
                "total_categories": len(CategoryManager.get_all_categories()),
                "rate_limits": {
                    "category_prediction": "20 requests per minute",
                    "form_submission": "10 submissions per minute",
                    "file_upload": "5 uploads per minute"
                }
            }

            return jsonify({
                "status": "success",
                "system_info": system_info
            }), 200

        except Exception as e:
            current_app.logger.error(f"System info retrieval error: {e}")
            return jsonify({
                "status": "error",
                "message": "Unable to retrieve system information"
            }), 500

    @staticmethod
    @general_bp.route('/api-capabilities', methods=['GET'])
    def get_api_capabilities():
        """
        Provide information about API capabilities
        
        Returns:
        JSON response with API capabilities
        """
        try:
            capabilities = {
                "legal_category_prediction": {
                    "description": "AI-powered legal category prediction",
                    "supported_methods": ["POST"],
                    "input_requirements": [
                        "Case summary text",
                        "PII removal applied"
                    ]
                },
                "form_generation": {
                    "description": "Dynamic form template generation",
                    "supported_methods": ["POST"],
                    "supported_categories": CategoryManager.get_all_categories()
                },
                "document_upload": {
                    "description": "Supporting document upload",
                    "max_file_size": "16 MB",
                    "supported_file_types": [
                        "txt", "pdf", "png", "jpg", 
                        "jpeg", "gif", "doc", "docx", 
                        "xls", "xlsx"
                    ]
                },
                "ai_powered_features": [
                    "Category prediction",
                    "Prompt generation",
                    "Confidence analysis",
                    "Alternative category suggestions"
                ]
            }

            return jsonify({
                "status": "success",
                "api_capabilities": capabilities
            }), 200

        except Exception as e:
            current_app.logger.error(f"API capabilities retrieval error: {e}")
            return jsonify({
                "status": "error",
                "message": "Unable to retrieve API capabilities"
            }), 500

# Global error handlers for general endpoints
@general_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@general_bp.errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 Method Not Allowed errors"""
    return jsonify({
        "status": "error",
        "message": "Method not allowed for this endpoint"
    }), 405

@general_bp.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server errors"""
    current_app.logger.error(f"General endpoint server error: {error}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500