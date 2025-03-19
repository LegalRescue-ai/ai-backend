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
            
            # Handle different possible formats of the summary result
            summary_text = summary_result.get('summary', '')
            
            # Check if the summary is in JSON format inside a code block
            json_block_pattern = r"```json\s*([\s\S]*?)\s*```"
            json_match = re.search(json_block_pattern, summary_text, re.DOTALL)
            
            if json_match:
                # Clean the JSON string by removing problematic control characters
                json_text = json_match.group(1)
                json_text = ''.join(ch for ch in json_text if ord(ch) >= 32 or ch in '\n\r\t')
                
                try:
                    # Try to parse the entire JSON block
                    summary_data = json.loads(json_text)
                    current_app.logger.info("Successfully parsed summary JSON block")
                except json.JSONDecodeError as e:
                    current_app.logger.warning(f"JSON parse error: {str(e)}")
                    
                    # If parsing fails, extract title and summary directly with regex
                    title_match = re.search(r'"title":\s*"([^"]*)"', json_text)
                    title = title_match.group(1) if title_match else "Untitled Case"
                    
                    summary_match = re.search(r'"summary":\s*"([\s\S]*?)"\s*\n}', json_text)
                    summary_html = ""
                    if summary_match:
                        # Clean up the escaping and normalize newlines
                        summary_html = summary_match.group(1)\
                            .replace('\\n', '\n')\
                            .replace('\\"', '"')\
                            .replace('\\t', '\t')
                        current_app.logger.info("Extracted HTML content using regex")
                    else:
                        current_app.logger.error("Failed to extract HTML content")
                        summary_html = summary_text  # Use the raw summary as fallback
                    
                    summary_data = {
                        "title": title,
                        "summary": summary_html
                    }
            else:
                # If no JSON block found, use the raw summary
                current_app.logger.warning("No JSON code block found, using raw summary")
                summary_data = {
                    "title": "Case Summary",  # Default title
                    "summary": summary_text   # Use raw summary text
                }
            
            # Extract list items from the HTML, handling potential capitalization differences
            html_content = summary_data.get('summary', '')
            
            # Try different possible section titles for key aspects (handle capitalization)
            key_aspects = extract_list_items(html_content, 'Key aspects of the case')
            if not key_aspects:  # If not found, try alternative capitalization
                key_aspects = extract_list_items(html_content, 'Key Aspects of the Case')
            if not key_aspects:  # Try another variation
                key_aspects = extract_list_items(html_content, 'Key Aspects')
                
            # Similarly for potential merits
            potential_merits = extract_list_items(html_content, 'Potential Merits of the Case')
            if not potential_merits:
                potential_merits = extract_list_items(html_content, 'Potential merits of the case')
            if not potential_merits:
                potential_merits = extract_list_items(html_content, 'Potential Merits')
                
            # And for critical factors
            critical_factors = extract_list_items(html_content, 'General Case Summary')
            if not critical_factors:
                critical_factors = extract_list_items(html_content, 'Case Summary')
                
            current_app.logger.info(f"Extracted key_aspects: {len(key_aspects)} items")
            current_app.logger.info(f"Extracted potential_merits: {len(potential_merits)} items")
            current_app.logger.info(f"Extracted critical_factors: {len(critical_factors)} items")
            
            # Initialize database service
            current_app.logger.info("Initializing database service")
            db_service = DatabaseService()  # This class now handles array formatting properly
            
            try:
                current_app.logger.info("Storing actual case data")
                case_data = {
                    "title": summary_data.get('title', 'Untitled Case'),
                    "summary": summary_data['summary'],
                    "keyAspects": key_aspects,
                    "potentialMerits": potential_merits,
                    "criticalFactors": critical_factors,
                    "CaseId": int(caseId),
                }
                
                stored_case = db_service.create_record('AI case submission', case_data)
                
                # Add the database ID to the response
                summary_result['case_id'] = stored_case[0]['id'] if stored_case and len(stored_case) > 0 else None
                summary_result['stored'] = True
                
                current_app.logger.info(f"Case summary stored with ID: {summary_result.get('case_id')}")
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                
               
            
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