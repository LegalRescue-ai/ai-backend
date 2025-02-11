import re
from typing import Dict, Any, List, Union, Optional
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class Validator:
    """Comprehensive validation utility for legal case management"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        cleaned_phone = re.sub(r'\D', '', phone)
        return len(cleaned_phone) in [10, 11]

    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate Social Security Number format"""
        cleaned_ssn = re.sub(r'\D', '', ssn)
        return len(cleaned_ssn) == 9 and cleaned_ssn not in {'000000000', '999999999'}

    @staticmethod
    def validate_date(input_date: Union[str, datetime, date], min_date: Optional[datetime] = None, max_date: Optional[datetime] = None) -> bool:
        """Validate date format and range"""
        try:
            if isinstance(input_date, str):
                input_date = datetime.fromisoformat(input_date)

            if isinstance(input_date, date) and not isinstance(input_date, datetime):
                input_date = datetime.combine(input_date, datetime.min.time())

            if min_date and input_date < min_date:
                return False

            if max_date and input_date > max_date:
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def validate_currency(amount: Union[str, float, int]) -> bool:
        """Validate currency amount"""
        try:
            if isinstance(amount, str):
                amount = float(re.sub(r'[^\d.-]', '', amount))
            return amount >= 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate personal name format"""
        return bool(re.match(r'^[A-Za-z\'\-\s]+$', name)) if name and len(name) > 1 else False

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate street address"""
        return bool(re.match(r'\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)', address, re.IGNORECASE)) if address and len(address) > 5 else False

    @staticmethod
    def validate_select(value: str, options: List[str]) -> bool:
        """Validate if value is in the allowed list"""
        return value in options

    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """Validate string length"""
        return isinstance(value, str) and min_length <= len(value) <= (max_length if max_length else len(value))

    @staticmethod
    def validate_number(value: Union[int, float], min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
        """Validate numeric values within a range"""
        try:
            num = float(value)
            return (min_value is None or num >= min_value) and (max_value is None or num <= max_value)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_passport(passport: str) -> bool:
        """Validate passport number format"""
        cleaned = re.sub(r'[\s\-]', '', passport)
        return 6 <= len(cleaned) <= 20 and bool(re.match(r'^[A-Z0-9]+$', cleaned, re.IGNORECASE))

    @staticmethod
    def validate_zip_code(zip_code: str) -> bool:
        """Validate US ZIP code format"""
        return bool(re.match(r'^\d{5}(-\d{4})?$', zip_code))

    @staticmethod
    def validate_bar_number(bar_number: str) -> bool:
        """Validate attorney bar number"""
        cleaned = re.sub(r'[\s\-]', '', bar_number)
        return 5 <= len(cleaned) <= 8 and bool(re.match(r'^[A-Z0-9]+$', cleaned, re.IGNORECASE))

    @staticmethod
    def validate_case_number(case_number: str) -> bool:
        """Validate legal case number"""
        cleaned = re.sub(r'[\s\-]', '', case_number)
        return bool(re.match(r'^(\d{2}|\d{4})[A-Z0-9]{5,10}$', cleaned, re.IGNORECASE))

    @staticmethod
    def validate_form_data(data: Dict[str, Any], validation_rules: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate form data against predefined validation rules"""
        validation_results = {
            "is_valid": True,
            "errors": {},
            "validated_data": {}
        }

        for field, rules in validation_rules.items():
            value = data.get(field)

            if rules.get('required', False) and not value:
                validation_results['is_valid'] = False
                validation_results['errors'][field] = "This field is required"
                continue

            if value is None:
                continue

            try:
                field_type = rules.get('type', 'str')

                if field_type == 'email' and not Validator.validate_email(str(value)):
                    raise ValidationError("Invalid email format", field)

                if field_type == 'phone' and not Validator.validate_phone(str(value)):
                    raise ValidationError("Invalid phone number", field)

                if field_type == 'date' and not Validator.validate_date(value, rules.get('min_date'), rules.get('max_date')):
                    raise ValidationError("Invalid date", field)

                if field_type == 'currency' and not Validator.validate_currency(value):
                    raise ValidationError("Invalid currency amount", field)

                if field_type == 'name' and not Validator.validate_name(str(value)):
                    raise ValidationError("Invalid name format", field)

                if field_type == 'address' and not Validator.validate_address(str(value)):
                    raise ValidationError("Invalid address format", field)

                if field_type == 'select' and not Validator.validate_select(str(value), rules.get('options', [])):
                    raise ValidationError("Invalid selection", field)

                if field_type == 'number' and not Validator.validate_number(value, rules.get('min'), rules.get('max')):
                    raise ValidationError("Invalid number", field)

                validation_results['validated_data'][field] = value

            except ValidationError as e:
                validation_results['is_valid'] = False
                validation_results['errors'][field] = e.message

        return validation_results

def validate_legal_form(form_data: Dict[str, Any], category: str, subcategory: str) -> Dict[str, Any]:
    """
    Validate a legal form's data based on category and subcategory rules.
    
    Args:
        form_data (Dict[str, Any]): Form input data.
        category (str): Legal category.
        subcategory (str): Legal subcategory.
    
    Returns:
        Dict[str, Any]: Validation results.
    """
    validation_rules = Validator.VALIDATION_RULES.get(category, {}).get(subcategory, {})
    return Validator.validate_form_data(form_data, validation_rules)
