from typing import Dict, Any, List
import openai
import json

class FormPrefillerService:
    """Service for pre-filling legal forms based on case analysis"""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def prefill_form(self, category: str, subcategory: str, initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pre-filled form data based on category and initial analysis

        Args:
            category (str): Selected legal category
            subcategory (str): Selected subcategory
            initial_analysis (Dict[str, Any]): Initial case analysis

        Returns:
            Dict containing pre-filled form fields
        """
        try:
            # Common fields across all forms
            common_fields = [
                "Age", "Occupation", "Marital Status", "Gross Annual Income", "Date of Incident", 
                "Relationship to Other Party", "Current Legal Status", "Planned Legal Action"
            ]

            # Constructing a precise and structured prompt with support for different field types
            prompt = f"""
            Extract and structure the necessary information to pre-fill a {category} - {subcategory} legal form.
            Ensure all extracted data is formatted in JSON with clearly labeled fields relevant to the form type.
            
            - Remove any Personally Identifiable Information (PII) such as names, addresses, and social security numbers.
            - Use US date format (MM/DD/YYYY) where applicable.
            - Include common legal form fields: {', '.join(common_fields)}.
            - Omit fields where data is unavailable or ambiguous.
            
            For selection fields with predefined options (radio buttons, checkboxes):
            - For single-select fields (radio buttons): Provide the exact option text that should be selected.
            - For multi-select fields (checkboxes): Provide an array of option texts that should be checked.
            
            Example format for different field types:
            {{
                "Age": "35",                                            // Text field
                "Marital Status": "Married",                            // Radio button selection
                "Legal Issues": ["Custody", "Child Support"],           // Checkbox selections
                "Date of Incident": "03/15/2024"                        // Date field
            }}
            
            Provided case details:
            {initial_analysis['cleaned_text']}
            """
            
            # Query GPT-4o for pre-filled form fields
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert legal assistant specializing in structured data extraction for legal forms. You can identify appropriate values for different types of form fields including text fields, radio buttons, and checkboxes."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            # Parse the AI-generated structured response
            prefilled_data = response.choices[0].message.content

            return {
                "status": "success",
                "prefilled_data": prefilled_data,
                "category": category,
                "subcategory": subcategory
            }

        except Exception as e:
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
        # Parse prefilled_data if it's a string
        if isinstance(prefilled_data, str):
            try:
                prefilled_data = json.loads(prefilled_data)
            except json.JSONDecodeError:
                return {"status": "error", "error": "Invalid JSON in prefilled data"}
                
        validated_data = {}
        
        for field, value in prefilled_data.items():
            if field in form_template:
                # Validate field value against template rules
                if self._validate_field(value, form_template[field]):
                    validated_data[field] = value

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
        # Basic validation based on field type
        field_type = field_rules.get("type", "text")
        
        # Text field validation
        if field_type == "text" and isinstance(value, str):
            return True
            
        # Number field validation
        elif field_type == "number":
            try:
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
            return value in options
            
        # Checkbox validation (multi-select)
        elif field_type == "checkbox" and isinstance(value, list):
            options = field_rules.get("options", [])
            return all(option in options for option in value)
            
        return True  # Default fallback for any other field types