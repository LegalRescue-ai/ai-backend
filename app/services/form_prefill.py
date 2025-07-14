from typing import Dict, Any, List
import openai
import json
import os

class FormPrefillerService:
    """Service for pre-filling legal forms based on case analysis"""

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
    
    def _load_forms_data(self, forms_path: str) -> Dict[str, Any]:
        """Load forms data from JSON file"""
        try:
            with open(forms_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading forms data: {str(e)}")
            return {}
    
    def get_form_template(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Get form template for specific category and subcategory"""
        try:
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
                    title = form.get("title", "")
                    if subcategory in title:
                        form_data = form
                        form_key = key
                        print(f"Found form with matching title: {key} - {title}")
                        break
            
            if not form_data:
                print(f"No matching form found for {category}/{subcategory}")
                return {
                    "title": f"{category} - {subcategory} Form",
                    "elements": []
                }
            
            # Return the complete form structure
            return form_data
            
        except Exception as e:
            print(f"Error retrieving form template: {str(e)}")
            return {
                "title": f"{category} - {subcategory} Form",
                "elements": []
            }
    
    def prefill_form(self, category: str, subcategory: str, initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pre-filled form data based on category and initial analysis

        Args:
            category (str): Selected legal category
            subcategory (str): Selected subcategory
            initial_analysis (Dict[str, Any]): Initial case analysis

        Returns:
            Dict containing pre-filled form fields and form structure
        """
        try:
            print(f"Prefilling form for {category}/{subcategory}")
            # Get the specific form template for this category/subcategory
            form_template = self.get_form_template(category, subcategory)
            
            if not form_template or not form_template.get("elements"):
                return {
                    "status": "error",
                    "error": f"No form template found for {category}/{subcategory}"
                }
            
            # Extract field information for the AI to use
            field_info = []
            for element in form_template.get("elements", []):
                field_name = element.get("name")
                field_type = element.get("type", "text")
                options = element.get("options", []) if field_type in ["radio", "checkbox"] else None
                
                if field_name:
                    field_info.append({
                        "name": field_name,
                        "title": element.get("title", ""),
                        "type": field_type,
                        "options": options
                    })
            
            # Get case text from whatever field is available
            case_text = ""
            if 'original_text' in initial_analysis and initial_analysis['original_text'].strip():
                case_text = initial_analysis['original_text']
            elif 'cleaned_text' in initial_analysis:
                case_text = initial_analysis['cleaned_text']
            else:
                # Try to find any text field we can use
                for key, value in initial_analysis.items():
                    if isinstance(value, str) and len(value) > 100:
                        case_text = value
                        break
            
            # Extract useful information for hints
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
            
            # Constructing a precise prompt for the AI
            prompt = f"""
            Extract and structure information to pre-fill a legal form for {category} - {subcategory}.
            Use the case details below to extract values for the following specific form fields:
            
            {json.dumps(field_info, indent=2)}
            
            Follow these guidelines:
            - Return ALL field names in your JSON response matching exactly the names provided above
            - Be proactive in filling fields when you have enough information to make an educated guess, while still being accurate
            - Only leave a field blank (empty string) when there is absolutely no information to work with
            - For professional information like occupation, extract the actual profession (e.g., 'software developer', 'nurse', 'accountant') from the context
            - Use US date format (MM/DD/YYYY) where applicable
            - For dates mentioned approximately (like "10 years ago" or "three years ago"), convert to an estimated date
            - For single-select fields (radio buttons): Select the most appropriate option based on the information provided
            - For multi-select fields (checkboxes): Include all options that apply based on the information
            
            Format your response as a valid JSON object with all field names from the template, providing the best possible values based on the available information.{occupation_hint}
            
            Case details:
            {case_text}
            """
            
            # Use a comprehensive system prompt
            system_prompt = """You are an expert legal assistant specializing in structured data extraction for legal forms. 
            Your job is to extract information from case details to fill in form fields.
            Be proactive about filling in fields where you have enough context to make a reasonable determination.
            For fields like occupation, disability type, employment status, and similar factual information, make your best assessment.
            For fields asking about preferences or future plans, use contextual clues when available.
            Only leave fields completely blank when you have absolutely no information to work with.
            IMPORTANT: Return ALL field names in your JSON response, even if the value is an empty string."""
            
            # Query GPT-4o for pre-filled form fields
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the AI-generated structured response
            prefilled_data_str = response.choices[0].message.content
            
            try:
                prefilled_data = json.loads(prefilled_data_str)
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
            
            # Serialize the prefilled data
            prefilled_data_str = json.dumps(prefilled_data)
            
            # Return the response with both the prefilled data and form structure
            response_data = {
                "status": "success",
                "prefilled_data": prefilled_data_str,
                "form_structure": form_template,  # Include the complete form structure
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
                "error": str(e)
            }

    def validate_prefilled_data(self, prefilled_data: Dict[str, Any], form_template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pre-filled data against form template

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
                field_rules[field_name] = {
                    "type": element.get("type", "text"),
                    "title": element.get("title", ""),
                    "options": element.get("options", [])
                }
        
        # If prefilled_data is already a dict, use it directly
        if not isinstance(prefilled_data, dict):
            try:
                prefilled_data = json.loads(prefilled_data) if isinstance(prefilled_data, str) else {}
            except json.JSONDecodeError:
                return {"status": "error", "error": "Invalid JSON in prefilled data"}
                
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
            print(f"Failed validations: {json.dumps(validation_results['failed'], indent=2)}")
        
        return validated_data

    def _validate_field(self, value: Any, field_rules: Dict[str, Any]) -> bool:
        """
        Validate a single field value against rules
        
        Args:
            value (Any): Field value to validate
            field_rules (Dict[str, Any]): Validation rules for the field
        
        Returns:
            bool: True if valid
        """
        if value is None or value == "":
            return True  # Empty values are considered valid now
            
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
            
        # Radio button validation (single select)
        elif field_type == "radio" and isinstance(value, str):
            options = field_rules.get("options", [])
            
            # Fix encoding issues in options
            cleaned_options = []
            for option in options:
                # Clean up any potential encoding issues (especially for em-dashes)
                cleaned_option = option.replace('â€"', '-')
                cleaned_options.append(cleaned_option)
            
            # Print options and value for debugging
            print(f"Validating radio option: '{value}'")
            print(f"Available options: {options}")
            print(f"Available options (cleaned): {cleaned_options}")
            
            # Check if the value is an exact match to any option or cleaned option
            if value in options or value in cleaned_options:
                return True
                
            # If not an exact match, check if it's contained in any option
            for option in options:
                if value in option:
                    print(f"Found partial match: '{value}' in '{option}'")
                    return True
                    
            # Also check in cleaned options
            for option in cleaned_options:
                if value in option:
                    print(f"Found partial match in cleaned option: '{value}' in '{option}'")
                    return True
                    
            return False
            
        # Checkbox validation (multi-select)
        elif field_type == "checkbox" and isinstance(value, list):
            options = field_rules.get("options", [])
            return all(option in options for option in value)
        
        # Checkbox validation for string format (comma-separated values)
        elif field_type == "checkbox" and isinstance(value, str):
            options = field_rules.get("options", [])
            selected_options = [opt.strip() for opt in value.split(',') if opt.strip()]
            return all(option in options for option in selected_options)
            
        return False  # Default to False if no validation rules match
