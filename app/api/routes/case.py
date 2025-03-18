from flask import Blueprint, jsonify, request, session, current_app
from app.services.case_analyzer import CaseAnalyzer
from app.services.form_prefill import FormPrefillerService
from app.services.database_service import DatabaseService
import json
import re

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
    Accepts completed form data, generates final summary and stores it in Supabase
    """
    try:
        current_app.logger.info("Starting generate_summary process")
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
        current_app.logger.info("Generating final summary")
        summary_result = analyzer.generate_final_summary(
            initial_analysis,
            data['form_data']
        )
        current_app.logger.info(f"Summary generated: {summary_result.get('status', 'unknown')}")

        # Process the summary for database storage
        try:
            current_app.logger.info("Processing summary for database storage")
            # Extract the JSON content from the summary string
            summary_json_str = re.search(r'```json\n(.*?)\n```', summary_result['summary'], re.DOTALL)
            if summary_json_str:
                summary_data = json.loads(summary_json_str.group(1))
                current_app.logger.info(f"Parsed summary JSON successfully")
                
                # Extract key aspects from HTML
                key_aspects = extract_list_items(summary_data['summary'], 'Key aspects of the case')
                key_aspects_str = ', '.join(key_aspects)  # Convert array to string
                current_app.logger.info(f"Extracted key_aspects: {len(key_aspects)} items")
                
                # Extract potential merits
                potential_merits = extract_list_items(summary_data['summary'], 'Potential Merits of the Case')
                potential_merits_str = ', '.join(potential_merits)  # Convert array to string
                current_app.logger.info(f"Extracted potential_merits: {len(potential_merits)} items")
                
                # Extract critical factors
                critical_factors = extract_list_items(summary_data['summary'], 'General Case Summary')
                critical_factors_str = ', '.join(critical_factors)  # Convert array to string
                current_app.logger.info(f"Extracted critical_factors: {len(critical_factors)} items")
                
                # Initialize database service
                current_app.logger.info("Initializing database service")
                db_service = DatabaseService()
                
                # Prepare case data for storage with correct data types
                case_data = {
                    "title": summary_data.get('title', 'Untitled Case'),
                    "summary": summary_data['summary'],  # Full HTML summary
                    "keyAspects": key_aspects_str,       # Store as text
                    "potentialMerits": potential_merits_str,  # Store as varchar
                    "criticalFactors": critical_factors_str,  # Store as varchar
                    # Additional useful data
                    "CaseId": data.get('case_id', 16),   # int8
                }
                
                current_app.logger.info(f"Prepared case data for storage: {case_data}")
                
                # Store in Supabase
                current_app.logger.info("Storing data in Supabase table 'AI case submission'")
                stored_case = db_service.create_record('AI case submission', case_data)
                
                # Add the database ID to the response
                summary_result['case_id'] = stored_case[0]['id'] if stored_case else None
                summary_result['stored'] = True
                
                current_app.logger.info(f"Case summary stored with ID: {summary_result.get('case_id')}")
                
            else:
                current_app.logger.error("Failed to parse summary JSON from response")
                summary_result['stored'] = False
                summary_result['storage_error'] = "Could not parse summary data"
                
        except Exception as db_error:
            current_app.logger.error(f"Error storing case summary: {str(db_error)}")
            # Still return the summary even if storage failed
            summary_result['stored'] = False
            summary_result['storage_error'] = str(db_error)

        return jsonify(summary_result), 200

    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def extract_list_items(html_content, section_title):
    """Extract list items from a specific section in the HTML content"""
    pattern = f"<h3>{section_title}</h3>\\s*<ul>(.+?)</ul>"
    section_match = re.search(pattern, html_content, re.DOTALL)
    
    if section_match:
        list_content = section_match.group(1)
        # Extract individual list items
        items = re.findall(r"<li>(.+?)</li>", list_content, re.DOTALL)
        return [item.strip() for item in items]
    
    return []


@case_bp.route('/cases', methods=['GET'])
def get_cases():
    """
    Get all cases from the database
    Optionally filter by user_id if provided
    """
    try:
        user_id = request.args.get('user_id')
        query = {'CaseId': user_id} if user_id else None
        
        db_service = DatabaseService()
        cases = db_service.get_records('AI case submission', query)
        
        return jsonify({
            "status": "success",
            "count": len(cases),
            "cases": cases
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching cases: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@case_bp.route('/cases/<case_id>', methods=['GET'])
def get_case_by_id(case_id):
    """
    Get a specific case by ID
    """
    try:
        db_service = DatabaseService()
        cases = db_service.get_records('AI case submission', {'id': case_id})
        
        if not cases:
            return jsonify({
                "status": "error",
                "message": "Case not found"
            }), 404
            
        return jsonify({
            "status": "success",
            "case": cases[0]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching case {case_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@case_bp.route('/test-db', methods=['GET'])
def test_db():
    """
    Test endpoint to verify database connectivity
    """
    try:
        db_service = DatabaseService()
        test_data = {
            "title": "Test Case",
            "summary": "<h3>Test Summary</h3>",
            "keyAspects": "Test aspect 1, Test aspect 2",
            "potentialMerits": "Test merit 1, Test merit 2",
            "criticalFactors": "Test factor 1, Test factor 2",
            "CaseId": 99
        }
        
        current_app.logger.info(f"Attempting to create test record in 'AI case submission'")
        result = db_service.create_record('AI case submission', test_data)
        current_app.logger.info(f"Test record created: {result}")
        
        return jsonify({
            "status": "success",
            "message": "Test record created",
            "data": result
        }), 200
    except Exception as e:
        current_app.logger.error(f"Test DB error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500