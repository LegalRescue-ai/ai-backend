import re
from typing import Union, Dict, Any
from datetime import datetime, date

class Formatter:
    """
    Comprehensive formatting utility for legal case management
    """

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Standardize phone number formatting
        
        Args:
            phone (str): Raw phone number
        
        Returns:
            str: Formatted phone number
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Handle different length scenarios
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if cannot be formatted

    @staticmethod
    def format_ssn(ssn: str) -> str:
        """
        Mask Social Security Number
        
        Args:
            ssn (str): Raw SSN
        
        Returns:
            str: Masked SSN
        """
        # Remove non-digit characters
        digits = re.sub(r'\D', '', ssn)
        
        if len(digits) == 9:
            return f"XXX-XX-{digits[-4:]}"
        return ssn

    @staticmethod
    def format_currency(amount: Union[int, float, str], currency: str = 'USD') -> str:
        """
        Format currency with locale-specific formatting
        
        Args:
            amount (Union[int, float, str]): Amount to format
            currency (str): Currency code
        
        Returns:
            str: Formatted currency string
        """
        try:
            # Convert to float if string
            if isinstance(amount, str):
                amount = float(re.sub(r'[^\d.-]', '', amount))
            
            # Format with two decimal places
            formatted = f"{amount:,.2f}"
            
            # Add currency symbol based on code
            currency_symbols = {
                'USD': '$',
                'EUR': '€',
                'GBP': '£',
                'JPY': '¥'
            }
            
            symbol = currency_symbols.get(currency, currency)
            return f"{symbol}{formatted}"
        
        except (ValueError, TypeError):
            return str(amount)

    @staticmethod
    def format_date(input_date: Union[str, datetime, date], format_type: str = 'standard') -> str:
        """
        Format dates consistently
        
        Args:
            input_date (Union[str, datetime, date]): Date to format
            format_type (str): Formatting style
        
        Returns:
            str: Formatted date string
        """
        # Convert input to datetime if it's a string
        if isinstance(input_date, str):
            try:
                input_date = datetime.fromisoformat(input_date)
            except ValueError:
                return input_date  # Return original if parsing fails
        
        # Ensure we're working with a datetime object
        if isinstance(input_date, date) and not isinstance(input_date, datetime):
            input_date = datetime.combine(input_date, datetime.min.time())
        
        # Format based on type
        formats = {
            'standard': '%m/%d/%Y',
            'long': '%B %d, %Y',
            'iso': '%Y-%m-%d',
            'friendly': '%b %d, %Y'
        }
        
        return input_date.strftime(formats.get(format_type, formats['standard']))

    @staticmethod
    def format_name(name: str, format_type: str = 'full') -> str:
        """
        Standardize name formatting
        
        Args:
            name (str): Name to format
            format_type (str): Formatting style
        
        Returns:
            str: Formatted name
        """
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Split name components
        parts = name.split()
        
        if format_type == 'initials':
            # Return initials
            return ''.join(part[0].upper() for part in parts)
        
        elif format_type == 'last_first':
            # Format as Last, First
            if len(parts) > 1:
                return f"{parts[-1].upper()}, {' '.join(parts[:-1]).title()}"
            return name.title()
        
        return name.title()

    @staticmethod
    def sanitize_input(input_data: str) -> str:
        """
        Sanitize input to prevent potential security risks
        
        Args:
            input_data (str): Input to sanitize
        
        Returns:
            str: Sanitized input
        """
        # Remove potential XSS and injection risks
        return re.sub(r'<[^>]+>', '', input_data).strip()

    @staticmethod
    def format_legal_reference(reference: str) -> str:
        """
        Format legal reference numbers consistently
        
        Args:
            reference (str): Reference number to format
        
        Returns:
            str: Formatted reference number
        """
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', reference)
        
        # Uppercase and add hypens if needed
        if len(cleaned) > 4:
            return f"{cleaned[:4]}-{cleaned[4:8]}-{cleaned[8:]}"
        
        return cleaned.upper()

def format_case_data(data: Dict[str, Any], category: str = None) -> Dict[str, Any]:
    """
    Comprehensive data formatting utility
    
    Args:
        data (Dict[str, Any]): Data to format
        category (str, optional): Legal category for specific formatting
    
    Returns:
        Dict with formatted data
    """
    formatted_data = {}
    
    # Define formatting rules
    formatting_rules = {
        'phone': Formatter.format_phone_number,
        'ssn': Formatter.format_ssn,
        'currency': Formatter.format_currency,
        'date': Formatter.format_date,
        'name': Formatter.format_name
    }
    
    # Apply formatting based on key patterns
    for key, value in data.items():
        # Check for specific formatting rules
        for pattern, formatter in formatting_rules.items():
            if pattern in key.lower():
                try:
                    formatted_data[key] = formatter(value)
                    break
                except Exception:
                    formatted_data[key] = value
        else:
            # Default case
            formatted_data[key] = value
    
    return formatted_data