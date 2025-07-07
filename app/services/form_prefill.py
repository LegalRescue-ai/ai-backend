from typing import Dict, Any, List
import openai
import json
import os
import html
import unicodedata

class FormPrefillerService:
    """Service for pre-filling legal forms based on case analysis - ENCODING SAFE"""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        # Path to forms data in the new data directory
        forms_path = os.path.join(os.path.dirname(__file__), "..", "data", "legalForms.json")
        self.forms_data = self._load_forms_data(forms_path)
        
        # Define mappings for categories and subcategories
        self.category_mapping = {
            "Family Law": "1",
            "Employment Law": "2",
            "Criminal Law": "3",
            "Real Estate Law": "4",
            "Business/Corporate Law": "5",
            "Immigration Law": "6",
            "Personal Injury Law": "7",
            "Wills, Trusts, & Estates Law": "8",
            "Bankruptcy, Finances, & Tax Law": "9",
            "Government & Administrative Law": "10",
            "Product & Services Liability Law": "11",
            "Intellectual Property Law": "12",
            "Landlord/Tenant Law": "13"
        }
        
        self.subcategory_mapping = {
            # Family Law (category 1)
            "Adoptions": "1",
            "Child Custody & Visitation": "2",
            "Child Support": "3",
            "Divorce": "4",
            "Guardianship": "5",
            "Paternity": "6",
            "Separations": "7",
            "Spousal Support or Alimony": "8",
            
            # Employment Law (category 2)
            "Disabilities": "1",
            "Employment Contracts": "2",
            "Employment Discrimination": "3",
            "Pensions and Benefits": "4",
            "Sexual Harassment": "5",
            "Wages and Overtime Pay": "6",
            "Workplace Disputes": "7",
            "Wrongful Termination": "8",
            
            # Criminal Law (category 3)
            "General Criminal Defense": "1",
            "Environmental Violations": "2",
            "Drug Crimes": "3",
            "Drunk Driving/DUI/DWI": "4",
            "Felonies": "5",
            "Misdemeanors": "6",
            "Speeding and Moving Violations": "7",
            "White Collar Crime": "8",
            "Tax Evasion": "9",
            
            # Real Estate Law (category 4)
            "Commercial Real Estate": "1",
            "Condominiums and Cooperatives": "2",
            "Construction Disputes": "3",
            "Foreclosures": "4",
            "Mortgages": "5",
            "Purchase and Sale of Residence": "6",
            "Title and Boundary Disputes": "7",
            
            # Business/Corporate Law (category 5)
            "Breach of Contract": "1",
            "Corporate Tax": "2",
            "Business Disputes": "3",
            "Buying and Selling a Business": "4",
            "Contract Drafting and Review": "5",
            "Corporations, LLCs, Partnerships, etc.": "6",
            "Entertainment Law": "7",
            
            # Immigration Law (category 6)
            "Citizenship": "1",
            "Deportation": "2",
            "Permanent Visas or Green Cards": "3",
            "Temporary Visas": "4",
            
            # Personal Injury Law (category 7)
            "Automobile Accidents": "1",
            "Dangerous Property or Buildings": "2",
            "Defective Products": "3",
            "Medical Malpractice": "4",
            "Personal Injury (General)": "5",
            
            # Wills, Trusts, & Estates Law (category 8)
            "Contested Wills or Probate": "1",
            "Drafting Wills and Trusts": "2",
            "Estate Administration": "3",
            "Estate Planning": "4",
            
            # Bankruptcy, Finances, & Tax Law (category 9)
            "Collections": "1",
            "Consumer Bankruptcy": "2",
            "Consumer Credit": "3",
            "Income Tax": "4",
            "Property Tax": "5",
            "Repossessions": "6",
            "Creditors' or Debtors' Rights": "7",
            
            # Government & Administrative Law (category 10)
            "Education and Schools": "1",
            "Social Security – Disability": "2",
            "Social Security – Retirement": "3",
            "Social Security – Dependent Benefits": "4",
            "Social Security – Survivor Benefits": "5",
            "Veterans Benefits": "6",
            "General Administrative Law": "7",
            "Environmental Law": "8",
            "Liquor Licenses": "9",
            "Constitutional Law": "10",
            
            # Product & Services Liability Law (category 11)
            "Attorney Malpractice": "1",
            "Defective Products": "2",
            "Warranties": "3",
            "Consumer Protection and Fraud": "4",
            
            # Intellectual Property Law (category 12)
            "Copyright": "1",
            "Patents": "2",
            "Trademarks": "3",
            
            # Landlord/Tenant Law (category 13)
            "General Landlord and Tenant Issues": "1"
        }

    # ENCODING SAFETY FUNCTIONS
    def _safe_encode_text(self, text: str) -> str:
        """Safely encode text for form display"""
        if not text:
            return ""
        
        try:
            # Normalize Unicode characters
            text = unicodedata.normalize('NFKC', text)
            
            # Replace problematic Unicode characters
            text = text.replace('\u00a0', ' ')    # Non-breaking space
            text = text.replace('\u2013', '-')    # En dash
            text = text.replace('\u2014', '--')   # Em dash
            text = text.replace('\u2018', "'")    # Left single quote
            text = text.replace('\u2019', "'")    # Right single quote
            text = text.replace('\u201c', '"')    # Left double quote
            text = text.replace('\u201d', '"')    # Right double quote
            text = text.replace('â€"', '-')       # Broken encoding em-dash
            text = text.replace('â€™', "'")       # Broken encoding apostrophe
            text = text.replace('â€œ', '"')       # Broken encoding left quote
            text = text.replace('â€\x9d', '"')    # Broken encoding right quote
            
            # Ensure valid UTF-8
            encoded = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            # HTML escape for safe form display
            return html.escape(encoded, quote=False)
            
        except Exception as e:
            print(f"Text encoding error: {e}")
            # Fallback: keep only ASCII characters
            return ''.join(char for char in text if ord(char) < 128)

    def _safe_json_dumps(self, data: Any, **kwargs) -> str:
        """Safely serialize JSON for form display"""
        try:
            # Force ASCII encoding to prevent form display issues
            return json.dumps(data, ensure_ascii=True, **kwargs)
        except (TypeError, ValueError) as e:
            print(f"JSON serialization error: {e}")
            # Fallback: convert to string representation
            return json.dumps(str(data), ensure_ascii=True)

    def _clean_form_data(self, data: Any) -> Any:
        """Recursively clean all text data for safe form display"""
        if isinstance(data, dict):
            return {key: self._clean_form_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_form_data(item) for item in data]
        elif isinstance(data, str):
            return self._safe_encode_text(data)
        else:
            return data

    def _normalize_option_text(self, text: str) -> str:
        """Normalize option text for comparison"""
        if not text:
            return ""
        
        # Clean and normalize
        cleaned = self._safe_encode_text(text)
        
        # Additional normalizations for option matching
        cleaned = cleaned.replace('–', '-')    # En dash to hyphen
        cleaned = cleaned.replace('—', '--')   # Em dash to double hyphen
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _load_forms_data(self, forms_path: str) -> Dict[str, Any]:
        """Load forms data from JSON file with encoding safety"""
        try:
            with open(forms_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Clean all loaded form data
                return self._clean_form_data(data)
        except Exception as e:
            print(f"Error loading forms data: {str(e)}")
            return {}
    
    def get_form_template(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Get form template for specific category and subcategory - encoding safe"""
        try:
            # Clean input parameters
            category = self._safe_encode_text(category)
            subcategory = self._safe_encode_text(subcategory)
            
            # First, try to map the text categories to numeric IDs
            numeric_category = self.category_mapping.get(category, "")
            numeric_subcategory = self.subcategory_mapping.get(subcategory, "")
            
            # Try different key formats to find the form
            possible_keys = []
            
            # Add all possible key combinations
            if numeric_category and numeric_subcategory:
                possible_keys.append(f"{numeric_category}-{numeric_subcategory}")
            
            if category.isdigit() and subcategory.isdigit():
                possible_keys.append(f"{category}-{subcategory}")
                
            possible_keys.append(f"{category}-{subcategory}")
            
            # Try each possible key format
            form_data = None
            form_key = None
            
            for key in possible_keys:
                if key in self.forms_data:
                    form_data = self.forms_data[key]
                    form_key = key
                    print(f"Found form with key: {key}")
                    break
            
            # If still not found, search by title containing the subcategory
            if not form_data:
                print(f"Searching for form by title containing: {subcategory}")
                for key, form in self.forms_data.items():
                    title = self._safe_encode_text(form.get("title", ""))
                    if subcategory in title:
                        form_data = form
                        form_key = key
                        print(f"Found form with matching title: {key} - {title}")
                        break
            
            if not form_data:
                print(f"No matching form found for {category}/{subcategory}")
                return {
                    "title": self._safe_encode_text(f"{category} - {subcategory} Form"),
                    "elements": []
                }
            
            # Clean the form data before returning
            cleaned_form_data = self._clean_form_data(form_data)
            return cleaned_form_data
            
        except Exception as e:
            print(f"Error retrieving form template: {str(e)}")
            return {
                "title": self._safe_encode_text(f"{category} - {subcategory} Form"),
                "elements": []
            }
    
    def prefill_form(self, category: str, subcategory: str, initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pre-filled form data based on category and initial analysis - ENCODING SAFE

        Args:
            category (str): Selected legal category
            subcategory (str): Selected subcategory
            initial_analysis (Dict[str, Any]): Initial case analysis

        Returns:
            Dict containing pre-filled form fields and form structure
        """
        try:
            # Clean input parameters
            category = self._safe_encode_text(category)
            subcategory = self._safe_encode_text(subcategory)
            
            print(f"Prefilling form for {category}/{subcategory}")
            
            # Get the specific form template for this category/subcategory
            form_template = self.get_form_template(category, subcategory)
            
            if not form_template or not form_template.get("elements"):
                return {
                    "status": "error",
                    "error": f"No form template found for {category}/{subcategory}"
                }
            
            # Extract field information for the AI to use - with text cleaning
            field_info = []
            for element in form_template.get("elements", []):
                field_name = self._safe_encode_text(element.get("name", ""))
                field_type = element.get("type", "text")
                
                # Clean options if they exist
                options = None
                if field_type in ["radio", "checkbox"] and element.get("options"):
                    options = [self._safe_encode_text(opt) for opt in element.get("options", [])]
                
                if field_name:
                    field_info.append({
                        "name": field_name,
                        "title": self._safe_encode_text(element.get("title", "")),
                        "type": field_type,
                        "options": options
                    })
            
            # Get case text from whatever field is available - WITH CLEANING
            case_text = ""
            if 'original_text' in initial_analysis and initial_analysis['original_text'].strip():
                case_text = self._safe_encode_text(initial_analysis['original_text'])
            elif 'cleaned_text' in initial_analysis:
                case_text = self._safe_encode_text(initial_analysis['cleaned_text'])
            else:
                # Try to find any text field we can use
                for key, value in initial_analysis.items():
                    if isinstance(value, str) and len(value) > 100:
                        case_text = self._safe_encode_text(value)
                        break
            
            # Extract useful information for hints - with text cleaning
            occupation_hint = ""
            if case_text:
                useful_info = []
                
                # Look for occupation
                occupation_indicators = ["job title", "occupation", "profession", "works as", "employed as", "developer", "engineer"]
                for line in case_text.split("."):
                    line_lower = line.lower()
                    if any(indicator in line_lower for indicator in occupation_indicators):
                        useful_info.append(f"Occupation information: '{line.strip()}'")
                        break
                
                # Look for disability information
                disability_indicators = ["disability", "condition", "diagnosed", "health", "medical"]
                for line in case_text.split("."):
                    line_lower = line.lower()
                    if any(indicator in line_lower for indicator in disability_indicators):
                        useful_info.append(f"Disability information: '{line.strip()}'")
                        break
                
                # Look for employment status
                employment_indicators = ["employed", "working", "current job", "position"]
                for line in case_text.split("."):
                    line_lower = line.lower()
                    if any(indicator in line_lower for indicator in employment_indicators):
                        useful_info.append(f"Employment status information: '{line.strip()}'")
                        break
                
                if useful_info:
                    occupation_hint = "\n\nNote: The following information may be useful for filling the form:\n" + "\n".join(useful_info)
            
            # Constructing a precise prompt for the AI - with safe JSON
            prompt = f"""
            Extract and structure information to pre-fill a legal form for {category} - {subcategory}.
            Use the case details below to extract values for the following specific form fields:
            
            {self._safe_json_dumps(field_info, indent=2)}
            
            Follow these guidelines:
            - Return ALL field names in your JSON response matching exactly the names provided above
            - Be proactive in filling fields when you have enough information to make an educated guess, while still being accurate
            - Only leave a field blank (empty string) when there is absolutely no information to work with
            - For professional information like occupation, extract the actual profession (e.g., 'software developer', 'nurse', 'accountant') from the context
            - Use US date format (MM/DD/YYYY) where applicable
            - For dates mentioned approximately (like "10 years ago" or "three years ago"), convert to an estimated date
            - For single-select fields (radio buttons): Select the most appropriate option based on the information provided
            - For multi-select fields (checkboxes): Include all options that apply based on the information
            - IMPORTANT: Use only ASCII characters in your response to avoid encoding issues
            
            Format your response as a valid JSON object with all field names from the template, providing the best possible values based on the available information.{occupation_hint}
            
            Case details:
            {case_text}
            """
            
            # Use a comprehensive system prompt - emphasizing ASCII output
            system_prompt = """You are an expert legal assistant specializing in structured data extraction for legal forms. 
            Your job is to extract information from case details to fill in form fields.
            Be proactive about filling in fields where you have enough context to make a reasonable determination.
            For fields like occupation, disability type, employment status, and similar factual information, make your best assessment.
            For fields asking about preferences or future plans, use contextual clues when available.
            Only leave fields completely blank when you have absolutely no information to work with.
            IMPORTANT: Return ALL field names in your JSON response, even if the value is an empty string.
            CRITICAL: Use only ASCII characters in your response to ensure proper form display."""
            
            # Query GPT-4o for pre-filled form fields
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent output
            )
            
            # Parse the AI-generated structured response - WITH CLEANING
            prefilled_data_str = response.choices[0].message.content
            prefilled_data_str = self._safe_encode_text(prefilled_data_str)
            
            try:
                prefilled_data = json.loads(prefilled_data_str)
                # Clean all prefilled data
                prefilled_data = self._clean_form_data(prefilled_data)
                print(f"Prefilled data fields: {list(prefilled_data.keys())}")
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": prefilled_data_str
                }
            
            # Ensure all fields from the form template are in the prefilled data
            for element in form_template.get("elements", []):
                field_name = element.get("name")
                if field_name and field_name not in prefilled_data:
                    prefilled_data[field_name] = ""
            
            # Remove fields that don't exist in the form template
            form_field_names = [element.get("name") for element in form_template.get("elements", [])]
            mismatched_fields = [field for field in prefilled_data.keys() if field not in form_field_names]
            if mismatched_fields:
                print(f"WARNING: AI returned fields that don't exist in the form: {mismatched_fields}")
                for field in mismatched_fields:
                    prefilled_data.pop(field, None)
            
            # Serialize the prefilled data with safe encoding
            prefilled_data_str = self._safe_json_dumps(prefilled_data)
            
            # Return the response with both the prefilled data and form structure
            response_data = {
                "status": "success",
                "prefilled_data": prefilled_data_str,
                "form_structure": form_template,  # Already cleaned in get_form_template
                "category": category,
                "subcategory": subcategory
            }
            
            print(f"Returning form structure with {len(form_template.get('elements', []))} elements")
            return response_data

        except Exception as e:
            import traceback
            print(f"Error in prefill_form: {str(e)}")
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": self._safe_encode_text(str(e))
            }

    def validate_prefilled_data(self, prefilled_data: Dict[str, Any], form_template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pre-filled data against form template - ENCODING SAFE

        Args:
            prefilled_data (Dict[str, Any]): Pre-filled form data
            form_template (Dict[str, Any]): Form template with field definitions

        Returns:
            Dict containing validated data
        """
        # Convert form_template elements to a dict for easier validation
        field_rules = {}
        for element in form_template.get("elements", []):
            field_name = element.get("name")
            if field_name:
                # Clean all form template data
                field_rules[field_name] = {
                    "type": element.get("type", "text"),
                    "title": self._safe_encode_text(element.get("title", "")),
                    "options": [self._safe_encode_text(opt) for opt in element.get("options", [])]
                }
        
        # If prefilled_data is already a dict, use it directly, otherwise parse
        if not isinstance(prefilled_data, dict):
            try:
                prefilled_data = json.loads(prefilled_data) if isinstance(prefilled_data, str) else {}
            except json.JSONDecodeError:
                return {"status": "error", "error": "Invalid JSON in prefilled data"}
        
        # Clean all prefilled data
        prefilled_data = self._clean_form_data(prefilled_data)
        
        validated_data = {}
        
        # Track validation results for debugging
        validation_results = {"passed": [], "failed": []}
        
        for field_name, value in prefilled_data.items():
            if field_name in field_rules:
                # Skip validation for empty values
                if value == "":
                    validated_data[field_name] = value
                    validation_results["passed"].append(field_name)
                    continue
                
                # Validate field value against template rules
                if self._validate_field(value, field_rules[field_name]):
                    validated_data[field_name] = value
                    validation_results["passed"].append(field_name)
                else:
                    print(f"Validation failed for field: {field_name}")
                    print(f"  Value provided: {value}")
                    print(f"  Field rules: {field_rules[field_name]}")
                    validation_results["failed"].append({
                        "field": field_name,
                        "value": value,
                        "expected_type": field_rules[field_name].get("type"),
                        "options": field_rules[field_name].get("options", [])
                    })
                    # For failed validations, include the field with an empty value
                    validated_data[field_name] = ""
            else:
                print(f"Field not in template: {field_name}")
                validation_results["failed"].append({
                    "field": field_name,
                    "reason": "Field not in template"
                })
        
        # Ensure all form fields are included in the validated data
        for field_name in field_rules.keys():
            if field_name not in validated_data:
                validated_data[field_name] = ""
        
        print(f"Validation summary - Passed: {len(validation_results['passed'])}, Failed: {len(validation_results['failed'])}")
        if validation_results["failed"]:
            print(f"Failed validations: {self._safe_json_dumps(validation_results['failed'], indent=2)}")
        
        return validated_data

    def _validate_field(self, value: Any, field_rules: Dict[str, Any]) -> bool:
        """
        Validate a single field value against rules - ENCODING SAFE
        
        Args:
            value (Any): Field value to validate
            field_rules (Dict[str, Any]): Validation rules for the field
        
        Returns:
            bool: True if valid
        """
        if value is None or value == "":
            return True  # Empty values are considered valid
        
        # Clean the value for validation
        if isinstance(value, str):
            value = self._safe_encode_text(value)
            
        # Basic validation based on field type
        field_type = field_rules.get("type", "text")
        
        # Text field validation
        if field_type == "text" and isinstance(value, str):
            return True
            
        # Number field validation
        elif field_type == "number":
            try:
                # Accept both numerical strings and actual numbers
                if isinstance(value, str):
                    float(value)
                return True
            except (ValueError, TypeError):
                return False
                
        # Date field validation (simple format check)
        elif field_type == "date" and isinstance(value, str):
            # Basic date format validation could be added here
            return True
            
        # Radio button validation (single select) - ENCODING SAFE
        elif field_type == "radio" and isinstance(value, str):
            options = field_rules.get("options", [])
            
            # Normalize the input value
            normalized_value = self._normalize_option_text(value)
            
            # Normalize all options for comparison
            normalized_options = [self._normalize_option_text(opt) for opt in options]
            
            print(f"Validating radio option: '{normalized_value}'")
            print(f"Available options (normalized): {normalized_options}")
            
            # Check for exact match in normalized options
            if normalized_value in normalized_options:
                return True
                
            # Check for partial matches in normalized options
            for norm_option in normalized_options:
                if normalized_value in norm_option or norm_option in normalized_value:
                    print(f"Found partial match: '{normalized_value}' <-> '{norm_option}'")
                    return True
                    
            return False
            
        # Checkbox validation (multi-select) - ENCODING SAFE
        elif field_type == "checkbox" and isinstance(value, list):
            options = field_rules.get("options", [])
            normalized_options = [self._normalize_option_text(opt) for opt in options]
            normalized_values = [self._normalize_option_text(v) for v in value]
            return all(norm_val in normalized_options for norm_val in normalized_values)
        
        # Checkbox validation for string format (comma-separated values) - ENCODING SAFE
        elif field_type == "checkbox" and isinstance(value, str):
            options = field_rules.get("options", [])
            normalized_options = [self._normalize_option_text(opt) for opt in options]
            
            selected_options = [self._normalize_option_text(opt.strip()) for opt in value.split(',') if opt.strip()]
            return all(norm_opt in normalized_options for norm_opt in selected_options)
            
        return False  # Default to False if no validation rules match

    def get_form_safe_prefill(self, category: str, subcategory: str, initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get form prefill with additional encoding safety for display
        
        Args:
            category (str): Legal category
            subcategory (str): Legal subcategory  
            initial_analysis (Dict[str, Any]): Case analysis data
            
        Returns:
            Dict with form-safe prefilled data
        """
        try:
            # Get the standard prefill
            result = self.prefill_form(category, subcategory, initial_analysis)
            
            if result.get("status") == "success":
                # Additional safety layer for form display
                
                # Re-clean the prefilled data
                if isinstance(result.get("prefilled_data"), str):
                    try:
                        prefilled_dict = json.loads(result["prefilled_data"])
                        cleaned_prefilled = self._clean_form_data(prefilled_dict)
                        result["prefilled_data"] = self._safe_json_dumps(cleaned_prefilled)
                    except json.JSONDecodeError:
                        pass
                
                # Clean form structure
                if result.get("form_structure"):
                    result["form_structure"] = self._clean_form_data(result["form_structure"])
                
                # Clean category/subcategory
                result["category"] = self._safe_encode_text(result.get("category", ""))
                result["subcategory"] = self._safe_encode_text(result.get("subcategory", ""))
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": self._safe_encode_text(str(e))
            }