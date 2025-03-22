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
        caseId = data.get('caseId')

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
            
            # Get the summary text from the result
            summary_text = summary_result.get('summary', '')
            
            # Check if the summary is in JSON format
            try:
                # First, try to parse it directly as JSON
                if isinstance(summary_text, str):
                    summary_data = json.loads(summary_text)
                    current_app.logger.info("Successfully parsed summary JSON")
                else:
                    summary_data = summary_text
                    
                # Extract title
                title = summary_data.get('title', 'Untitled Case')
                
                # Extract the summary sections
                summary_sections = summary_data.get('summary', {})
                
                # Extract the different sections
                # Each section should be an array of strings
                case_summary = summary_sections.get('General Case Summary', [])
                key_aspects = summary_sections.get('Key aspects of the case', [])
                
                # Try alternative capitalization if not found
                if not key_aspects:
                    key_aspects = summary_sections.get('Key Aspects of the Case', [])
                if not key_aspects:
                    key_aspects = summary_sections.get('Key Aspects', [])
                
                potential_merits = summary_sections.get('Potential Merits of the Case', [])
                if not potential_merits:
                    potential_merits = summary_sections.get('Potential merits of the case', [])
                if not potential_merits:
                    potential_merits = summary_sections.get('Potential Merits', [])
                
                critical_factors = summary_sections.get('Critical factors', [])
                if not critical_factors:
                    critical_factors = summary_sections.get('Critical Factors', [])
                
                current_app.logger.info(f"Extracted case_summary: {len(case_summary)} items")
                current_app.logger.info(f"Extracted key_aspects: {len(key_aspects)} items")
                current_app.logger.info(f"Extracted potential_merits: {len(potential_merits)} items")
                current_app.logger.info(f"Extracted critical_factors: {len(critical_factors)} items")
                
            except json.JSONDecodeError as e:
                current_app.logger.warning(f"JSON parse error: {str(e)}")
                
                # If we couldn't parse the JSON, use regex as fallback
                # This approach is kept from the original implementation as a fallback
                json_block_pattern = r"```json\s*([\s\S]*?)\s*```"
                json_match = re.search(json_block_pattern, summary_text, re.DOTALL)
                
                if json_match:
                    # Clean the JSON string 
                    json_text = json_match.group(1)
                    json_text = ''.join(ch for ch in json_text if ord(ch) >= 32 or ch in '\n\r\t')
                    
                    try:
                        # Try to parse the JSON block
                        summary_data = json.loads(json_text)
                        current_app.logger.info("Successfully parsed summary JSON block")
                        
                        # Extract title and summary as before
                        title = summary_data.get('title', 'Untitled Case')
                        summary_sections = summary_data.get('summary', {})
                        
                        # Extract the different sections
                        case_summary = summary_sections.get('General Case Summary', "")
                        key_aspects = summary_sections.get('Key aspects of the case', [])
                        potential_merits = summary_sections.get('Potential Merits of the Case', [])
                        critical_factors = summary_sections.get('Critical factors', [])
                        
                    except json.JSONDecodeError:
                        # If still can't parse, use regex to extract each section
                        current_app.logger.warning("Falling back to regex extraction")
                        title = "Case Summary"  # Default title
                        
                        # Using empty arrays as default
                        case_summary = ""
                        key_aspects = []
                        potential_merits = []
                        critical_factors = []
                else:
                    # If no JSON block found, use default values
                    current_app.logger.warning("No JSON structure found, using defaults")
                    title = "Case Summary"
                    case_summary = ""
                    key_aspects = []
                    potential_merits = []
                    critical_factors = []
            
            # Initialize database service
            current_app.logger.info("Initializing database service")
            db_service = DatabaseService()
            
            try:
                current_app.logger.info("Storing case data")
                case_data = {
                    "title": title,
                    "summary": case_summary,
                    "keyAspects": key_aspects,
                    "potentialMerits": potential_merits,
                    "criticalFactors": critical_factors,
                    "CaseId": caseId,
                }
                
                stored_case = db_service.create_record('AI_case_submission', case_data)
                
                # Add the database ID to the response
                summary_result['case_id'] = stored_case[0]['id'] if stored_case and len(stored_case) > 0 else None
                summary_result['stored'] = True
                
                current_app.logger.info(f"Case summary stored with ID: {summary_result.get('case_id')}")
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                summary_result['stored'] = False
                summary_result['db_error'] = str(db_error)
            
        except Exception as process_error:
            current_app.logger.error(f"Error processing summary: {str(process_error)}")
            summary_result['stored'] = False
            summary_result['processing_error'] = str(process_error)

        return jsonify(summary_result), 200

    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
def extract_list_items(html_content, section_title):
    """Extract list items from a specific section in the HTML content"""
    # Escape any special regex characters in the section title
    escaped_title = re.escape(section_title)
    pattern = f"<h3>{escaped_title}</h3>\\s*<ul>(.+?)</ul>"
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
        query = {'CaseId': int(user_id)} if user_id else None
        
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
        
        # Create a minimal test record
        test_data = {
            "title": ["Test Case"],
            "summary": "<h3>Test Summary</h3>",
            "keyAspects": ["Test aspect 1"],  # Single item array
            "potentialMerits": ["Test merit 1"],  # Single item array 
            "criticalFactors": ["Test factor 1"],  # Single item array
            "CaseId": 14
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