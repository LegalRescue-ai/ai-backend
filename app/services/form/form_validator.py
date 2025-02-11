from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime, date
import logging

class FormValidationError(Exception):
    """Custom exception for form validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class FormValidator:
    """
    Comprehensive form validation utility for legal case management
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize FormValidator with optional logger
        
        Args:
            logger (Optional[logging.Logger]): Logger for validation messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def validate_form(self, form_data: Dict[str, Any], validation_rules: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate form data against comprehensive validation rules
        
        Args:
            form_data (Dict[str, Any]): Form data to validate
            validation_rules (Dict[str, Dict[str, Any]]): Validation rules for each field
        
        Returns:
            Dict with validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": {},
            "validated_data": {}
        }

        # Validate each field against its rules
        for field_name, rules in validation_rules.items():
            try:
                # Get field value (use None if not present)
                value = form_data.get(field_name)
                
                # Validate each rule for the field
                validated_value = self._validate_field(field_name, value, rules)
                
                # Store validated value
                validation_results['validated_data'][field_name] = validated_value
            
            except FormValidationError as e:
                # Capture validation errors
                validation_results['is_valid'] = False
                validation_results['errors'][e.field or field_name] = e.message

        return validation_results

    def _validate_field(self, field_name: str, value: Any, rules: Dict[str, Any]) -> Any:
        """
        Validate an individual field
        
        Args:
            field_name (str): Name of the field
            value (Any): Value to validate
            rules (Dict[str, Any]): Validation rules for the field
        
        Returns:
            Validated and potentially transformed value
        
        Raises:
            FormValidationError if validation fails
        """
        # Check if field is required
        if rules.get('required', False):
            if value is None or (isinstance(value, str) and not value.strip()):
                raise FormValidationError("This field is required", field_name)

        # Skip further validation if value is None and not required
        if value is None:
            return None

        # Type conversion and validation
        try:
            value = self._convert_type(field_name, value, rules.get('type', 'str'))
        except FormValidationError as e:
            raise e

        # Specific type validations
        validations = {
            'str': self._validate_string,
            'int': self._validate_number,
            'float': self._validate_number,
            'date': self._validate_date,
            'email': self._validate_email,
            'phone': self._validate_phone,
            'select': self._validate_select
        }

        # Get type-specific validation method
        type_validator = validations.get(rules.get('type', 'str'))
        if type_validator:
            try:
                value = type_validator(field_name, value, rules)
            except FormValidationError as e:
                raise e

        return value

    def _convert_type(self, field_name: str, value: Any, expected_type: str) -> Any:
        """
        Convert value to expected type
        
        Args:
            field_name (str): Name of the field
            value (Any): Value to convert
            expected_type (str): Expected type
        
        Returns:
            Converted value
        
        Raises:
            FormValidationError if conversion fails
        """
        try:
            if expected_type == 'str':
                return str(value).strip()
            elif expected_type == 'int':
                return int(value)
            elif expected_type == 'float':
                return float(value)
            elif expected_type == 'date':
                # Handle various date input formats
                if isinstance(value, (datetime, date)):
                    return value
                elif isinstance(value, str):
                    try:
                        return datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        raise FormValidationError(f"Invalid date format. Use YYYY-MM-DD", field_name)
            return value
        except (ValueError, TypeError):
            raise FormValidationError(f"Cannot convert to {expected_type}", field_name)

    def _validate_string(self, field_name: str, value: str, rules: Dict[str, Any]) -> str:
        """
        Validate string fields
        
        Args:
            field_name (str): Name of the field
            value (str): String value to validate
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated string
        
        Raises:
            FormValidationError if validation fails
        """
        # Minimum length check
        if 'min_length' in rules and len(value) < rules['min_length']:
            raise FormValidationError(
                f"Minimum length is {rules['min_length']} characters", 
                field_name
            )

        # Maximum length check
        if 'max_length' in rules and len(value) > rules['max_length']:
            raise FormValidationError(
                f"Maximum length is {rules['max_length']} characters", 
                field_name
            )

        # Regex pattern check
        if 'pattern' in rules:
            if not re.match(rules['pattern'], value):
                raise FormValidationError(
                    "Value does not match required pattern", 
                    field_name
                )

        return value

    def _validate_number(self, field_name: str, value: Union[int, float], rules: Dict[str, Any]) -> Union[int, float]:
        """
        Validate numeric fields
        
        Args:
            field_name (str): Name of the field
            value (Union[int, float]): Numeric value to validate
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated number
        
        Raises:
            FormValidationError if validation fails
        """
        # Minimum value check
        if 'min' in rules and value < rules['min']:
            raise FormValidationError(
                f"Minimum value is {rules['min']}", 
                field_name
            )

        # Maximum value check
        if 'max' in rules and value > rules['max']:
            raise FormValidationError(
                f"Maximum value is {rules['max']}", 
                field_name
            )

        return value

    def _validate_date(self, field_name: str, value: date, rules: Dict[str, Any]) -> date:
        """
        Validate date fields
        
        Args:
            field_name (str): Name of the field
            value (date): Date value to validate
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated date
        
        Raises:
            FormValidationError if validation fails
        """
        # Minimum date check
        if 'min_date' in rules and value < rules['min_date']:
            raise FormValidationError(
                f"Date cannot be before {rules['min_date']}", 
                field_name
            )

        # Maximum date check
        if 'max_date' in rules and value > rules['max_date']:
            raise FormValidationError(
                f"Date cannot be after {rules['max_date']}", 
                field_name
            )

        return value

    def _validate_email(self, field_name: str, value: str, rules: Dict[str, Any]) -> str:
        """
        Validate email fields
        
        Args:
            field_name (str): Name of the field
            value (str): Email value to validate
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated email
        
        Raises:
            FormValidationError if validation fails
        """
        # Email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            raise FormValidationError(
                "Invalid email format", 
                field_name
            )

        return value

    def _validate_phone(self, field_name: str, value: str, rules: Dict[str, Any]) -> str:
        """
        Validate phone number fields
        
        Args:
            field_name (str): Name of the field
            value (str): Phone number to validate
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated phone number
        
        Raises:
            FormValidationError if validation fails
        """
        # Remove non-digit characters
        cleaned_phone = re.sub(r'\D', '', value)
        
        # Check phone number length
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            raise FormValidationError(
                "Invalid phone number length", 
                field_name
            )

        return cleaned_phone

    def _validate_select(self, field_name: str, value: str, rules: Dict[str, Any]) -> str:
        """
        Validate select/dropdown fields
        
        Args:
            field_name (str): Name of the field
            value (str): Selected value
            rules (Dict[str, Any]): Validation rules
        
        Returns:
            Validated select value
        
        Raises:
            FormValidationError if validation fails
        """
        # Check if options are defined
        if 'options' in rules:
            if value not in rules['options']:
                raise FormValidationError(
                    f"Invalid selection. Must be one of {rules['options']}", 
                    field_name
                )

        return value

    def sanitize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data to prevent potential security risks
        
        Args:
            input_data (Dict[str, Any]): Input data to sanitize
        
        Returns:
            Sanitized input data
        """
        sanitized_data = {}
        for key, value in input_data.items():
            # Remove any potentially harmful HTML or script tags
            if isinstance(value, str):
                sanitized_value = re.sub(r'<[^>]+>', '', value)
                sanitized_data[key] = sanitized_value.strip()
            else:
                sanitized_data[key] = value
        
        return sanitized_data

# Example usage function
def validate_legal_form(form_data: Dict[str, Any], category: str, subcategory: str) -> Dict[str, Any]:
    """
    Utility function to validate a legal form with comprehensive validation rules
    
    Args:
        form_data (Dict[str, Any]): Form data to validate
        category (str): Legal category
        subcategory (str): Legal subcategory
    
    Returns:
        Dict with validation results
    """
    # Define comprehensive validation rules for all categories
    validation_rules = {
        "Family Law": {
            "Divorce": {
                "marriage_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "separation_date": {
                    "type": "date",
                    "required": False,
                    "max_date": datetime.now().date()
                },
                "children_count": {
                    "type": "int",
                    "min": 0,
                    "max": 20
                },
                "spouse_name": {
                    "type": "str",
                    "required": True,
                    "min_length": 2,
                    "max_length": 100
                }
            },
            "Child Custody & Visitation": {
                "child_age": {
                    "type": "int",
                    "required": True,
                    "min": 0,
                    "max": 18
                },
                "current_arrangement": {
                    "type": "select",
                    "required": True,
                    "options": ["Full Custody", "Joint Custody", "Visitation Rights", "None"]
                }
            },
            "Adoptions": {
                "child_birthdate": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "adoption_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Domestic", "International", "Stepparent", "Agency"]
                }
            }
        },
        "Employment Law": {
            "Wrongful Termination": {
                "employment_start_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "termination_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "employer_name": {
                    "type": "str",
                    "required": True,
                    "min_length": 2,
                    "max_length": 100
                }
            },
            "Workplace Disputes": {
                "incident_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "dispute_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Harassment", "Discrimination", "Wage Dispute", "Safety Concern"]
                }
            }
        },
        "Criminal Law": {
            "Drug Crimes": {
                "arrest_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "charge_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Possession", "Distribution", "Manufacturing", "Trafficking"]
                }
            },
            "DUI/DWI": {
                "incident_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "bac_level": {
                    "type": "float",
                    "required": True,
                    "min": 0,
                    "max": 1
                }
            }
        },
        "Real Estate Law": {
            "Purchase and Sale of Residence": {
                "property_address": {
                    "type": "str",
                    "required": True,
                    "min_length": 10,
                    "max_length": 200
                },
                "purchase_price": {
                    "type": "float",
                    "required": True,
                    "min": 0
                },
                "closing_date": {
                    "type": "date",
                    "required": True
                }
            },
            "Foreclosures": {
                "default_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "loan_amount": {
                    "type": "float",
                    "required": True,
                    "min": 0
                }
            }
        },
        "Immigration Law": {
            "Citizenship": {
                "residence_start_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "current_status": {
                    "type": "select",
                    "required": True,
                    "options": ["Green Card", "Visa", "Undocumented", "Other"]
                }
            },
            "Deportation": {
                "notice_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "current_location": {
                    "type": "str",
                    "required": True
                }
            }
        },
        "Personal Injury Law": {
            "Automobile Accidents": {
                "accident_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "injury_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Minor", "Serious", "Catastrophic", "Fatal"]
                },
                "medical_expenses": {
                    "type": "float",
                    "required": True,
                    "min": 0
                }
            },
            "Medical Malpractice": {
                "incident_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "healthcare_provider": {
                    "type": "str",
                    "required": True,
                    "min_length": 2,
                    "max_length": 100
                }
            }
        },
        "Bankruptcy Law": {
            "Consumer Bankruptcy": {
                "total_debt": {
                    "type": "float",
                    "required": True,
                    "min": 0
                },
                "bankruptcy_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Chapter 7", "Chapter 13"]
                },
                "previous_bankruptcy": {
                    "type": "select",
                    "required": True,
                    "options": ["Yes", "No"]
                }
            }
        },
        "Intellectual Property Law": {
            "Patents": {
                "invention_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "patent_status": {
                    "type": "select",
                    "required": True,
                    "options": ["Not Filed", "Pending", "Granted", "Rejected"]
                }
            },
            "Trademarks": {
                "first_use_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "mark_type": {
                    "type": "select",
                    "required": True,
                    "options": ["Word Mark", "Design Mark", "Combined Mark"]
                }
            }
        },
        "Landlord/Tenant Law": {
            "Evictions": {
                "lease_start_date": {
                    "type": "date",
                    "required": True
                },
                "last_payment_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                },
                "notice_served_date": {
                    "type": "date",
                    "required": True,
                    "max_date": datetime.now().date()
                }
            }
        }
    }

    # Common fields for all forms
    common_rules = {
        "full_name": {
            "type": "str",
            "required": True,
            "min_length": 2,
            "max_length": 100
        },
        "email": {
            "type": "email",
            "required": True
        },
        "phone": {
            "type": "phone",
            "required": True
        },
        "description": {
            "type": "str",
            "required": True,
            "min_length": 50,
            "max_length": 5000
        }
    }

    # Get specific validation rules or use default
    category_rules = validation_rules.get(category, {}).get(subcategory, {})
    
    # Combine common rules with category-specific rules
    combined_rules = {**common_rules, **category_rules}
    
    # Sanitize input first
    sanitized_data = FormValidator().sanitize_input(form_data)
    
    # Validate form
    validator = FormValidator()
    return validator.validate_form(sanitized_data, combined_rules)