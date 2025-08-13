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
    try:
        data = request.get_json()
        if not data or 'form_data' not in data:
            return jsonify({
                "status": "error", 
                "message": "Form data is required"
            }), 400

        initial_analysis = data.get('initial_analysis')
        caseId = data.get('caseId')

        if not initial_analysis:
            return jsonify({
                "status": "error",
                "message": "No initial analysis found. Please analyze the case first."
            }), 400

        analyzer = CaseAnalyzer(api_key=current_app.config['OPENAI_API_KEY'])
        summary_result = analyzer.generate_final_summary(initial_analysis, data['form_data'])
        
        if summary_result.get('status') != 'success':
            return jsonify(summary_result), 400

        summary_text = summary_result.get('summary', '')
        
        try:
            if isinstance(summary_text, str):
                summary_data = json.loads(summary_text)
            else:
                summary_data = summary_text

            title = summary_data.get('title', 'Untitled Case')
            summary_sections = summary_data.get('summary', {})
            
            case_summary = summary_sections.get('General Case Summary', '')
            key_aspects = summary_sections.get('Key aspects of the case', []) or summary_sections.get('Key Aspects', [])
            potential_merits = summary_sections.get('Potential Merits of the Case', []) or summary_sections.get('Potential Merits', [])
            critical_factors = summary_sections.get('Critical factors', []) or summary_sections.get('Critical Factors', [])
            
        except (json.JSONDecodeError, TypeError):
            title = "Case Summary"
            case_summary = ""
            key_aspects = []
            potential_merits = []
            critical_factors = []

        try:
            db_service = DatabaseService()
            case_data = {
                "title": title,
                "summary": case_summary,
                "keyAspects": key_aspects,
                "potentialMerits": potential_merits,
                "criticalFactors": critical_factors,
                "CaseId": caseId,
            }
            
            stored_case = db_service.create_record('AI_case_submission', case_data)
            
            summary_result.update({
                'case_id': stored_case[0]['id'] if stored_case else None,
                'stored': True
            })
            
        except Exception as db_error:
            summary_result.update({
                'stored': False,
                'db_error': str(db_error)
            })

        return jsonify(summary_result), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@case_bp.route('/generate-questionnaire-summary', methods=['POST'])
@monitor_performance
def generate_questionnaire_summary():
    """Ultra-optimized questionnaire summary generation - target under 5 seconds"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'form_data' not in data:
            return jsonify({"status": "error", "message": "Form data is required"}), 400

        form_data = data['form_data']
        category = data.get('category', 'Legal Matter')
        subcategory = data.get('subcategory', 'General Consultation')
        caseId = data.get('caseId')
        
        # Extract simplified data from new frontend structure
        client_name = form_data.get('client_name', 'Client')
        location = form_data.get('location', 'Unknown Location')
        case_summary = form_data.get('case_summary', '')[:800]  # Limit to 800 chars
        key_answers = form_data.get('key_answers', [])[:5]  # Only top 5 answers
        
        # OPTIMIZATION 1: Ultra-compressed prompt - 60% shorter than before
        prompt = f"""Legal summary for {category} - {subcategory}.
Client: {client_name}
Location: {location}
Case: {case_summary}
Key Info: {key_answers}

JSON:
{{
  "title": "Brief title (max 60 chars)",
  "summary": {{
    "General Case Summary": "2-3 sentences",
    "Key aspects of the case": ["Point 1", "Point 2", "Point 3"],
    "Potential Merits of the Case": ["Merit 1", "Merit 2", "Merit 3"],
    "Critical factors": ["Factor 1", "Factor 2", "Factor 3"]
  }}
}}"""

        # OPTIMIZATION 2: Aggressive API settings for maximum speed
        client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fastest model
            messages=[
                {"role": "system", "content": "Generate legal summaries as JSON. Be brief."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=500,  # Reduced from 800
            timeout=8  # Reduced from 15
        )

        summary_json = json.loads(response.choices[0].message.content)
        
        # OPTIMIZATION 3: Simplified data extraction
        title = summary_json.get('title', f"{category} Case")
        summary_sections = summary_json.get('summary', {})
        
        case_summary = summary_sections.get('General Case Summary', '')
        key_aspects = summary_sections.get('Key aspects of the case', [])
        potential_merits = summary_sections.get('Potential Merits of the Case', [])
        critical_factors = summary_sections.get('Critical factors', [])
        
        # OPTIMIZATION 4: Ultra-fast database operation - no complex error handling
        db_service = DatabaseService()
        case_data = {
            "title": title,
            "summary": case_summary,
            "keyAspects": key_aspects,
            "potentialMerits": potential_merits,
            "criticalFactors": critical_factors,
            "CaseId": caseId,
        }
        
        stored_case = db_service.create_record('AI_case_submission', case_data)
        case_id = stored_case[0]['id'] if stored_case and len(stored_case) > 0 else None
        
        total_time = time.time() - start_time
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": json.dumps(summary_json),
            "case_id": case_id,
            "stored": True,
            "method": "ultra_optimized",
            "processing_time": f"{total_time:.2f}s"
        }), 200
        
    except openai.Timeout:
        return jsonify({"status": "error", "message": "Request timeout"}), 408
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def extract_list_items(html_content, section_title):
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