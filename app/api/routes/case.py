from flask import Blueprint, jsonify, request, session, current_app
from app.services.case_analyzer import CaseAnalyzer
from app.services.form_prefill import FormPrefillerService
from app.services.database_service import DatabaseService
import json
import re

import uuid
import traceback
import openai
from datetime import datetime
import time
from functools import wraps

case_bp = Blueprint('case', __name__)

def monitor_performance(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        current_app.logger.info(f"{f.__name__} completed in {duration:.2f}s")
        return result
    return wrapper

@case_bp.route('/analyze', methods=['POST'])
def analyze_case():
    try:
        request_id = str(uuid.uuid4())[:8]
        current_app.logger.info(f"[{request_id}] NEW CASE ANALYSIS REQUEST")
        
        data = request.get_json()
        
        if not data or 'case_text' not in data:
            current_app.logger.error(f"[{request_id}] Missing case_text in request")
            return jsonify({
                "status": "error",
                "message": "Case text is required"
            }), 400

        case_text = data['case_text'].strip()
        
        if not case_text:
            return jsonify({
                "status": "error",
                "message": "Case text cannot be empty"
            }), 400
            
        common_greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        if case_text.lower() in common_greetings:
            return jsonify({
                "status": "error",
                "message": "Please provide details about your case instead of just a greeting."
            }), 400
            
        word_count = len(re.findall(r'\w+', case_text))
        
        if word_count < 10:
            return jsonify({
                "status": "error",
                "message": "Please provide more details about your case. We need at least 10 words to perform a meaningful analysis."
            }), 400

        repeating_chars = any(c * 10 in case_text for c in 'abcdefghijklmnopqrstuvwxyz')
        no_spaces = ' ' not in case_text and len(case_text) > 30
        
        if repeating_chars or no_spaces:
            return jsonify({
                "status": "error",
                "message": "Your input appears to contain gibberish or random text. Please provide a clear description of your legal case."
            }), 400
            
        words = re.findall(r'\w+', case_text.lower())
        unique_word_ratio = len(set(words)) / len(words) if words else 0
        extremely_high_ratio = unique_word_ratio > 0.98 and len(words) > 40
        
        if extremely_high_ratio:
            return jsonify({
                "status": "error",
                "message": "Your input appears to contain unusually random text. Please provide a clear description of your legal case."
            }), 400
        
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        analysis = analyzer.initial_analysis(data['case_text'])
        
        try:
            analysis_data = json.loads(analysis.get('analysis', '{}'))
            analysis_data['gibberish_detected'] = False
            
            if unique_word_ratio > 0.99 and len(words) > 50:
                analysis_data['gibberish_detected'] = True
            
            analysis['analysis'] = json.dumps(analysis_data)
            
            confidence = analysis_data.get('confidence')
            confidence_too_low = (
                confidence == 'low' or 
                (isinstance(confidence, (int, float)) and float(confidence) < 0.15)
            )
            
            if confidence_too_low:
                return jsonify({
                    "status": "error",
                    "message": "We're having trouble understanding your case description. Please provide more clear and specific details about your legal situation."
                }), 400
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            current_app.logger.warning(f"Error processing analysis confidence: {e}")
        
        session['initial_analysis'] = analysis
        return jsonify(analysis), 200

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        current_app.logger.error(f"[{error_id}] EXCEPTION in analyze_case: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error [{error_id}]: {str(e)}"
        }), 500


@case_bp.route('/prefill-form', methods=['POST'])
def prefill_form():
    try:
        data = request.get_json()
        if not data or 'category' not in data or 'subcategory' not in data:
            return jsonify({
                "status": "error",
                "message": "Category and subcategory are required"
            }), 400

        initial_analysis = data.get('initial_analysis')

        if not initial_analysis:
            return jsonify({
                "status": "error",
                "message": "No initial analysis found. Please analyze the case first."
            }), 400

        prefiller = FormPrefillerService(api_key=current_app.config['OPENAI_API_KEY'])
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
    Final summary generation endpoint.
    Generates final summary, stores it in AI_case_submission,
    and mirrors it to AI_case_submission_admin.
    Logs all steps and errors for debugging.
    """
    try:
        print(">>> Starting generate_summary process")
        current_app.logger.info("Starting generate_summary process")

        data = request.get_json()
        if not data or 'form_data' not in data:
            return jsonify({"status": "error", "message": "Form data is required"}), 400

        initial_analysis = data.get('initial_analysis')
        case_id = data.get('caseId')

        if not initial_analysis:
            return jsonify({"status": "error", "message": "No initial analysis found. Please analyze the case first."}), 400

        # Generate final summary
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        print(">>> Generating final summary")
        summary_result = analyzer.generate_final_summary(initial_analysis, data['form_data'])

        # Parse summary JSON safely
        def parse_summary(summary_text):
            if not summary_text:
                return "Case Summary", {}
            try:
                parsed = json.loads(summary_text) if isinstance(summary_text, str) else summary_text
                return parsed.get('title', 'Untitled Case'), parsed.get('summary', {})
            except json.JSONDecodeError:
                match = re.search(r"```json\s*([\s\S]*?)\s*```", summary_text, re.DOTALL)
                if match:
                    json_text = ''.join(ch for ch in match.group(1) if ord(ch) >= 32 or ch in '\n\r\t')
                    try:
                        parsed = json.loads(json_text)
                        return parsed.get('title', 'Untitled Case'), parsed.get('summary', {})
                    except json.JSONDecodeError:
                        return "Case Summary", {}
                return "Case Summary", {}

        title, summary_sections = parse_summary(summary_result.get('summary', ''))

        # Extract sections with fallback
        def extract_section(possible_keys, default=None):
            default = default or []
            for key in possible_keys:
                if key in summary_sections:
                    return summary_sections[key]
            return default

        case_summary = extract_section(['General Case Summary'], "")
        key_aspects = extract_section(['Key aspects of the case', 'Key Aspects'], [])
        potential_merits = extract_section(['Potential Merits of the Case', 'Potential Merits'], [])
        critical_factors = extract_section(['Critical factors', 'Critical Factors'], [])

        print(f">>> Extracted sections - summary: {case_summary}, key_aspects: {len(key_aspects)}, potential_merits: {len(potential_merits)}, critical_factors: {len(critical_factors)}")

        db_service = DatabaseService()

        # Prepare main case data
        case_data = {
            "title": title,
            "summary": case_summary,
            "keyAspects": key_aspects,
            "potentialMerits": potential_merits,
            "criticalFactors": critical_factors,
            "CaseId": case_id,
        }

        # Insert into main table
        print(">>> Inserting into AI_case_submission")
        stored_case = db_service.create_record('AI_case_submission', case_data)
        if not stored_case or len(stored_case) == 0:
            raise Exception("Failed to store case in AI_case_submission")

        print(">>> Successfully inserted main case")

        # Mirror to admin table
        print(">>> Inserting into AI_case_submission_admin")
        stored_admin_case = db_service.create_record('AI_case_submission_admin', stored_case[0])
        if not stored_admin_case or len(stored_admin_case) == 0:
            print(">>> Warning: Failed to store duplicate in AI_case_submission_admin")

        # Build response
        summary_result.update({
            "case_id": stored_case[0].get('id'),
            "admin_case_id": stored_admin_case[0].get('id') if stored_admin_case else None,
            "stored": bool(stored_case and stored_admin_case),
            "partial_storage": bool(stored_case) and not bool(stored_admin_case)
        })

        print(f">>> Response: {summary_result}")
        return jsonify(summary_result), 200

    except Exception as e:
        print(f">>> Error generating summary: {e}")
        current_app.logger.error(f"Error generating summary: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@case_bp.route('/generate-questionnaire-summary', methods=['POST'])
def generate_questionnaire_summary(): 
    """
    Fast questionnaire-based summary generation endpoint - QUESTIONNAIRE METHOD
    FIXED: Now uses EXACT SAME processing logic as AI method for database storage
    """
    try:
        request_id = str(uuid.uuid4())[:8]
        current_app.logger.info(f"[{request_id}] NEW QUESTIONNAIRE SUMMARY REQUEST")
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['form_data', 'caseId', 'category', 'subcategory', 'case_summary']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            current_app.logger.error(f"[{request_id}] Missing required fields: {missing_fields}")
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Extract data
        form_data = data['form_data']
        caseId = data['caseId']  # Use same variable name as AI method
        category = data['category'] 
        subcategory = data['subcategory']
        case_summary = data['case_summary']
        
        # Validate category/subcategory
        if not category or not subcategory:
            current_app.logger.error(f"[{request_id}] Invalid category/subcategory")
            return jsonify({
                'status': 'error',
                'message': 'Category and subcategory are required for questionnaire method'
            }), 400
        
        current_app.logger.info(f"[{request_id}] Processing questionnaire for {category} - {subcategory}")
        
        # Get analyzer instance
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        
        # Generate questionnaire-based summary (FAST PATH)
        current_app.logger.info(f"[{request_id}] Generating questionnaire summary")
        result = analyzer.generate_questionnaire_summary(
            form_data=form_data,
            case_summary=case_summary,
            category=category, 
            subcategory=subcategory
        )
        
        current_app.logger.info(f"[{request_id}] Questionnaire summary generated: {result.get('status', 'unknown')}")
        
        # FIXED: Create summary_result in EXACT same format as AI method
        summary_result = {
            "status": result.get("status", "success"),
            "timestamp": result.get("timestamp", datetime.utcnow().isoformat()),
            "summary": result.get("summary", ""),
            "confidence_score": result.get("confidence_score", 85),
            "confidence_label": result.get("confidence_label", "High")
        }
        
        # FIXED: Process the summary for database storage using EXACT SAME logic as AI method
        try:
            current_app.logger.info("Processing summary for database storage")
            
            # Get the summary text from the result (SAME as AI method)
            summary_text = summary_result.get('summary', '')
            
            # Check if the summary is in JSON format (SAME logic as AI method)
            try:
                # First, try to parse it directly as JSON (SAME as AI method)
                if isinstance(summary_text, str):
                    summary_data = json.loads(summary_text)
                    current_app.logger.info("Successfully parsed summary JSON")
                else:
                    summary_data = summary_text
                    
                # Extract title (SAME as AI method)
                title = summary_data.get('title', 'Untitled Case')
                
                # Extract the summary sections (SAME as AI method)
                summary_sections = summary_data.get('summary', {})
                
                # Extract the different sections (SAME logic as AI method)
                # Each section should be an array of strings
                case_summary = summary_sections.get('General Case Summary', [])
                key_aspects = summary_sections.get('Key aspects of the case', [])
                
                # Try alternative capitalization if not found (SAME as AI method)
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
                
                # If we couldn't parse the JSON, use regex as fallback (SAME as AI method)
                json_block_pattern = r"```json\s*([\s\S]*?)\s*```"
                json_match = re.search(json_block_pattern, summary_text, re.DOTALL)
                
                if json_match:
                    # Clean the JSON string (SAME as AI method)
                    json_text = json_match.group(1)
                    json_text = ''.join(ch for ch in json_text if ord(ch) >= 32 or ch in '\n\r\t')
                    
                    try:
                        # Try to parse the JSON block
                        summary_data = json.loads(json_text)
                        current_app.logger.info("Successfully parsed summary JSON block")
                        
                        # Extract title and summary as before (SAME as AI method)
                        title = summary_data.get('title', 'Untitled Case')
                        summary_sections = summary_data.get('summary', {})
                        
                        # Extract the different sections
                        case_summary = summary_sections.get('General Case Summary', "")
                        key_aspects = summary_sections.get('Key aspects of the case', [])
                        potential_merits = summary_sections.get('Potential Merits of the Case', [])
                        critical_factors = summary_sections.get('Critical factors', [])
                        
                    except json.JSONDecodeError:
                        # If still can't parse, use regex to extract each section (SAME as AI method)
                        current_app.logger.warning("Falling back to regex extraction")
                        title = "Case Summary"  # Default title
                        
                        # Using empty arrays as default
                        case_summary = ""
                        key_aspects = []
                        potential_merits = []
                        critical_factors = []
                else:
                    # If no JSON block found, use default values (SAME as AI method)
                    current_app.logger.warning("No JSON structure found, using defaults")
                    title = "Case Summary"
                    case_summary = ""
                    key_aspects = []
                    potential_merits = []
                    critical_factors = []
            
            # Initialize database service (SAME as AI method)
            current_app.logger.info("Initializing database service")
            db_service = DatabaseService()
            
            try:
                current_app.logger.info("Storing case data in both tables")
                # FIXED: Use EXACT SAME case_data structure as AI method
                case_data = {
                    "title": title,
                    "summary": case_summary,
                    "keyAspects": key_aspects,
                    "potentialMerits": potential_merits,
                    "criticalFactors": critical_factors,
                    "CaseId": caseId,
                }
                
                # First store in the main table (SAME as AI method)
                stored_case = db_service.create_record('AI_case_submission', case_data)
                
                if stored_case and len(stored_case) > 0:
                    # Get the ID from the main table insertion
                    main_id = stored_case[0]['id']
                    
                    # Add the ID to the data for the admin table
                    admin_case_data = case_data.copy()
                    admin_case_data['id'] = main_id
                    
                    # Store in admin table with the same ID (SAME as AI method)
                    stored_admin_case = db_service.create_record('AI_case_submission_admin', admin_case_data)

                    # Add the database IDs to the response (SAME as AI method)
                    summary_result['case_id'] = stored_case[0]['id'] if stored_case and len(stored_case) > 0 else None
                    summary_result['admin_case_id'] = stored_admin_case[0]['id'] if stored_admin_case and len(stored_admin_case) > 0 else None
                    summary_result['stored'] = bool(stored_case and stored_admin_case)
                    
                    current_app.logger.info(f"Case summary stored with IDs: {summary_result.get('case_id')} (main) and {summary_result.get('admin_case_id')} (admin)")
                    
                    if not stored_case or not stored_admin_case:
                        summary_result['partial_storage'] = True
                        if not stored_case:
                            current_app.logger.warning("Failed to store in AI_case_submission")
                        if not stored_admin_case:
                            current_app.logger.warning("Failed to store in AI_case_submission_admin")
                else:
                    summary_result['stored'] = False
                    current_app.logger.warning("Failed to store in AI_case_submission")
                    
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                summary_result['stored'] = False
                summary_result['db_error'] = str(db_error)
            
        except Exception as process_error:
            current_app.logger.error(f"Error processing summary: {str(process_error)}")
            summary_result['stored'] = False
            summary_result['processing_error'] = str(process_error)

        # Return response in EXACT SAME FORMAT as AI method
        return jsonify(summary_result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_questionnaire_summary: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def extract_list_items(html_content, section_title):
    """Helper function to extract list items from HTML content"""
    escaped_title = re.escape(section_title)
    pattern = f"<h3>{escaped_title}</h3>\\s*<ul>(.+?)</ul>"
    section_match = re.search(pattern, html_content, re.DOTALL)
    
    if section_match:
        list_content = section_match.group(1)
        items = re.findall(r"<li>(.+?)</li>", list_content, re.DOTALL)
        return [item.strip() for item in items]
    
    return []


@case_bp.route('/cases', methods=['GET'])
def get_cases():
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
    try:
        db_service = DatabaseService()
        
        test_data = {
            "title": ["Test Case"],
            "summary": "<h3>Test Summary</h3>",
            "keyAspects": ["Test aspect 1"],
            "potentialMerits": ["Test merit 1"],
            "criticalFactors": ["Test factor 1"],
            "CaseId": 14
        }
        
        result = db_service.create_record('AI case submission', test_data)
        
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

# Export the blueprint - this is what your main.py imports
api_bp = case_bp