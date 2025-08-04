from flask import Blueprint, jsonify, request, session, current_app
from app.services.case_analyzer import CaseAnalyzer
from app.services.form_prefill import FormPrefillerService
from app.services.database_service import DatabaseService
import json
import re
import uuid
import traceback

case_bp = Blueprint('case', __name__)


@case_bp.route('/analyze', methods=['POST'])
def analyze_case():
    """
    Initial case analysis endpoint with enhanced debugging
    Accepts raw case text and returns suggested category/subcategory
    """
    try:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        current_app.logger.info(f"🔍 [{request_id}] NEW CASE ANALYSIS REQUEST")
        
        data = request.get_json()
        current_app.logger.info(f"📊 [{request_id}] Request data keys: {list(data.keys()) if data else 'None'}")
        
        if not data or 'case_text' not in data:
            current_app.logger.error(f"❌ [{request_id}] Missing case_text in request")
            return jsonify({
                "status": "error",
                "message": "Case text is required"
            }), 400

        case_text = data['case_text'].strip()
        current_app.logger.info(f"📝 [{request_id}] Case text length: {len(case_text)} chars")
        current_app.logger.info(f"📝 [{request_id}] First 100 chars: '{case_text[:100]}...'")
        
        # Basic validation
        if not case_text:
            current_app.logger.error(f"❌ [{request_id}] Empty case text")
            return jsonify({
                "status": "error",
                "message": "Case text cannot be empty"
            }), 400
            
        # Check for common greetings only
        common_greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        if case_text.lower() in common_greetings:
            current_app.logger.error(f"❌ [{request_id}] Greeting detected: {case_text}")
            return jsonify({
                "status": "error",
                "message": "Please provide details about your case instead of just a greeting."
            }), 400
            
        # Check for minimum word count
        word_count = len(re.findall(r'\w+', case_text))
        current_app.logger.info(f"📊 [{request_id}] Word count: {word_count}")
        
        if word_count < 10:
            current_app.logger.error(f"❌ [{request_id}] Insufficient word count: {word_count}")
            return jsonify({
                "status": "error",
                "message": "Please provide more details about your case. We need at least 10 words to perform a meaningful analysis."
            }), 400

        # IMPROVED GIBBERISH DETECTION (much less aggressive)
        current_app.logger.info(f"🔍 [{request_id}] Running gibberish detection...")
        
        # Check for excessive repeating characters (much more relaxed)
        repeating_chars = any(c * 10 in case_text for c in 'abcdefghijklmnopqrstuvwxyz')  # Changed from 5 to 10
        current_app.logger.info(f"📊 [{request_id}] Repeating chars (10+) check: {repeating_chars}")
        
        # Check for lack of spaces (but allow some flexibility)
        no_spaces = ' ' not in case_text and len(case_text) > 30  # Only flag if very long AND no spaces
        current_app.logger.info(f"📊 [{request_id}] No spaces check: {no_spaces}")
        
        if repeating_chars or no_spaces:
            current_app.logger.warning(f"⚠️ [{request_id}] Basic gibberish detected - repeating: {repeating_chars}, no_spaces: {no_spaces}")
            return jsonify({
                "status": "error",
                "message": "Your input appears to contain gibberish or random text. Please provide a clear description of your legal case."
            }), 400
            
        # Calculate unique word ratio (much more permissive)
        words = re.findall(r'\w+', case_text.lower())
        unique_word_ratio = len(set(words)) / len(words) if words else 0
        current_app.logger.info(f"📊 [{request_id}] Unique word ratio: {unique_word_ratio:.3f} ({len(set(words))}/{len(words)})")
        
        # Much more permissive thresholds - only catch truly random text
        extremely_high_ratio = unique_word_ratio > 0.98 and len(words) > 40  # Very high bar
        current_app.logger.info(f"📊 [{request_id}] Extremely high ratio check: {extremely_high_ratio}")
        
        if extremely_high_ratio:
            current_app.logger.warning(f"⚠️ [{request_id}] Extreme unique word ratio detected: {unique_word_ratio:.3f}")
            return jsonify({
                "status": "error",
                "message": "Your input appears to contain unusually random text. Please provide a clear description of your legal case."
            }), 400
            
        current_app.logger.info(f"✅ [{request_id}] Gibberish detection passed")
        
        # Initialize analyzer
        current_app.logger.info(f"🤖 [{request_id}] Initializing CaseAnalyzer...")
        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        current_app.logger.info(f"📊 [{request_id}] Analyzing case with {word_count} words")
        
        # Perform initial analysis
        current_app.logger.info(f"🔬 [{request_id}] Starting OpenAI analysis...")
        analysis = analyzer.initial_analysis(data['case_text'])
        current_app.logger.info(f"📊 [{request_id}] Analysis result status: {analysis.get('status')}")
        
        # Check if the analysis result contains confidence information
        try:
            analysis_data = json.loads(analysis.get('analysis', '{}'))
            current_app.logger.info(f"📊 [{request_id}] Analysis data keys: {list(analysis_data.keys())}")
            
            # Add gibberish detection flag (very permissive now)
            gibberish_detected = False
            
            # Only flag as gibberish if EXTREMELY high unique word ratio
            if unique_word_ratio > 0.99 and len(words) > 50:  # Only truly random text
                current_app.logger.warning(f"⚠️ [{request_id}] Setting gibberish_detected=True due to extreme ratio: {unique_word_ratio:.3f}")
                gibberish_detected = True
                
            # Add the gibberish detection flag to the analysis
            analysis_data['gibberish_detected'] = gibberish_detected
            current_app.logger.info(f"📊 [{request_id}] Final gibberish_detected: {gibberish_detected}")
            
            # Update the analysis
            analysis['analysis'] = json.dumps(analysis_data)
            
            # Much less aggressive confidence check
            confidence = analysis_data.get('confidence')
            current_app.logger.info(f"📊 [{request_id}] Confidence: {confidence}")
            
            # Only reject if confidence is extremely low or explicitly marked as low
            confidence_too_low = (
                confidence == 'low' or 
                (isinstance(confidence, (int, float)) and float(confidence) < 0.15)  # Very low threshold
            )
            
            if confidence_too_low:
                current_app.logger.warning(f"⚠️ [{request_id}] Rejecting due to very low confidence: {confidence}")
                return jsonify({
                    "status": "error",
                    "message": "We're having trouble understanding your case description. Please provide more clear and specific details about your legal situation."
                }), 400
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            current_app.logger.warning(f"⚠️ [{request_id}] Error processing analysis confidence: {e}")
        
        # Store analysis in Flask's session
        session['initial_analysis'] = analysis
        current_app.logger.info(f"✅ [{request_id}] Analysis completed successfully")

        return jsonify(analysis), 200

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        current_app.logger.error(f"🚨 [{error_id}] EXCEPTION in analyze_case: {str(e)}")
        current_app.logger.error(f"🚨 [{error_id}] Traceback: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error [{error_id}]: {str(e)}"
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
        current_app.logger.info("Storing case data")
        # Extract summary fields from summary_result
        title = summary_result.get("title")
        case_summary = summary_result.get("summary")
        key_aspects = summary_result.get("keyAspects")
        potential_merits = summary_result.get("potentialMerits")
        critical_factors = summary_result.get("criticalFactors")

        case_data = {
            "title": title,
            "summary": case_summary,
            "keyAspects": key_aspects,
            "potentialMerits": potential_merits,
            "criticalFactors": critical_factors,
            "CaseId": caseId,
        }
        
        try:
            db_service = DatabaseService()
            # Save to the first table
            stored_case = db_service.create_record('AI_case_submission', case_data)
            
            if not stored_case or not stored_case[0] or 'id' not in stored_case[0]:
                raise Exception("Failed to create record in AI_case_submission")
            
            # Get the ID of the newly created record
            new_record_id = stored_case[0]['id']
            current_app.logger.info(f"Created record in AI_case_submission with ID: {new_record_id}")
            
            # Create the same record in the admin table with the same ID
            admin_case_data = dict(case_data)  # make a copy
            admin_case_data['id'] = new_record_id  # use the same ID
            
            # Save to the admin table
            admin_stored_case = db_service.create_record('AI_case_submission_admin', admin_case_data)
            
            if not admin_stored_case or not admin_stored_case[0]:
                raise Exception("Failed to create record in AI_case_submission_admin")
            
            # Add the database ID to the response
            summary_result['case_id'] = new_record_id
            summary_result['stored'] = True

            current_app.logger.info(f"Case summary stored in both tables with ID: {new_record_id}")
        except Exception as db_error:
            current_app.logger.error(f"Database error: {str(db_error)}")
            summary_result['stored'] = False
            summary_result['db_error'] = str(db_error)

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