from flask import Blueprint, jsonify, request, session, current_app


from app.services.case_analyzer import CaseAnalyzer
from app.services.form_prefill import FormPrefillerService


case_bp = Blueprint('case', __name__)



@case_bp.route('/analyze', methods=['POST'])
def analyze_case():
    """
    Initial case analysis endpoint
    Accepts raw case text and returns suggested category/subcategory
    """
    try:
        data = request.get_json()
        if not data or 'case_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Case text is required"
            }), 400

        # Initialize analyzer
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        print(analyzer)
        
        # Perform initial analysis
        analysis = analyzer.initial_analysis(data['case_text'])
        
        
        # ✅ Store analysis in Flask's session
        session['initial_analysis'] = analysis  # Use session instead of request.session

        return jsonify(analysis), 200

    except Exception as e:
        current_app.logger.error(f"Error analyzing case: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@case_bp.route('/prefill-form', methods=['POST'])
def prefill_form():
    """
    Form prefill endpoint
    Accepts category/subcategory and returns pre-filled form data
    """
    try:
        data = request.get_json()
        print("data from request", data)
        if not data or 'category' not in data or 'subcategory' not in data:
            return jsonify({
                "status": "error",
                "message": "Category and subcategory are required"
            }), 400

        # Get initial analysis from session
        initial_analysis = data.get('initial_analysis')

        if not initial_analysis:
            return jsonify({
                "status": "error",
                "message": "No initial analysis found. Please analyze the case first."
            }), 400

        # Initialize form prefiller
        prefiller = FormPrefillerService(api_key=current_app.config['OPENAI_API_KEY'])
        
        # Generate pre-filled form data
        prefilled_data = prefiller.prefill_form(
            data['category'],
            data['subcategory'],
            initial_analysis
        )

        return jsonify(prefilled_data), 200

    except Exception as e:
        current_app.logger.error(f"Error prefilling form: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@case_bp.route('/generate-summary', methods=['POST'])
def generate_summary():
    """
    Final summary generation endpoint
    Accepts completed form data and generates final summary
    """
    try:
        data = request.get_json()
        if not data or 'form_data' not in data:
            return jsonify({
                "status": "error",
                "message": "Form data is required"
            }), 400

        # Get initial analysis from session
        initial_analysis = data.get('initial_analysis')

        if not initial_analysis:
            return jsonify({
                "status": "error",
                "message": "No initial analysis found. Please analyze the case first."
            }), 400

        # Initialize analyzer
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        
        # Generate final summary
        summary = analyzer.generate_final_summary(
            initial_analysis,
            data['form_data']
        )

        return jsonify(summary), 200

    except Exception as e:
        current_app.logger.error(f"Error generating summary: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500