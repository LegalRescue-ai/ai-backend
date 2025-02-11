import re
import logging

class PIIRemover:
    """
    Utility class for removing Personally Identifiable Information (PII)
    from text using advanced regex patterns
    """
    
    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Remove PII from the given text
        
        Args:
            text (str): Input text to clean
        
        Returns:
            str: Text with PII removed
        """
        try:
            # Comprehensive PII removal patterns
            pii_patterns = [
                # Names (First Last)
                (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]'),
                
                # Dates (mm/dd/yyyy, mm-dd-yyyy, etc.)
                (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[DATE]'),
                
                # Email addresses
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
                
                # Phone numbers (various formats)
                (r'\b(?:\+\d{1,2}\s?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]'),
                
                # Street addresses
                (r'\d+\s+[A-Z][a-z]+(?: [A-Z][a-z]+)?\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', '[ADDRESS]'),
                
                # Social Security Numbers
                (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
                
                # Credit Card Numbers (basic pattern)
                (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]')
            ]
            
            # Apply each pattern
            cleaned_text = text
            for pattern, replacement in pii_patterns:
                cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
            
            return cleaned_text
        
        except Exception as e:
            logging.error(f"PII removal error: {e}")
            return text

    @classmethod
    def mask_sensitive_data(cls, data: dict) -> dict:
        """
        Mask sensitive data in a dictionary
        
        Args:
            data (dict): Input dictionary
        
        Returns:
            dict: Dictionary with sensitive data masked
        """
        masked_data = {}
        sensitive_keys = [
            'name', 'email', 'phone', 'address', 
            'ssn', 'credit_card', 'birthdate'
        ]
        
        for key, value in data.items():
            # Mask sensitive keys
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked_data[key] = cls.clean_text(str(value))
            else:
                masked_data[key] = value
        
        return masked_data