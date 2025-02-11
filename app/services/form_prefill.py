from typing import Dict, Any
import openai

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

            # Constructing a precise and structured prompt
            prompt = f"""
            Extract and structure the necessary information to pre-fill a {category} - {subcategory} legal form.
            Ensure all extracted data is formatted in JSON with clearly labeled fields relevant to the form type.
            
            - Remove any Personally Identifiable Information (PII) such as names, addresses, and social security numbers.
            - Use US date format (MM/DD/YYYY) where applicable.
            - Include common legal form fields: {', '.join(common_fields)}.
            - Omit fields where data is unavailable or ambiguous.
            
            Provided case details:
            {initial_analysis['cleaned_text']}
            """
            
            # Query GPT-4o for pre-filled form fields
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert legal assistant specializing in structured data extraction for legal forms."},
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
        # Implement field validation logic based on rules
        # This is a placeholder - implement actual validation
        return True