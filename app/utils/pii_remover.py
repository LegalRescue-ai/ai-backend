import re
import logging

class PIIRemover:
    """
    Legal-context-aware PII remover that preserves important case information
    while protecting privacy
    """
    
    # Legal terms and medical terms to preserve
    PRESERVE_TERMS = {
        'medical': [
            'doctor', 'dr', 'surgeon', 'physician', 'nurse', 'medical', 'hospital',
            'clinic', 'patient', 'surgery', 'device', 'treatment', 'diagnosis',
            'medication', 'prescription', 'therapy', 'procedure', 'operation'
        ],
        'business': [
            'business', 'company', 'corporation', 'llc', 'inc', 'partner', 'customer',
            'client', 'vendor', 'supplier', 'contractor', 'employee', 'employer',
            'manager', 'supervisor', 'ceo', 'president', 'director'
        ],
        'legal': [
            'attorney', 'lawyer', 'judge', 'court', 'lawsuit', 'contract', 'agreement',
            'plaintiff', 'defendant', 'witness', 'evidence', 'trial', 'hearing',
            'settlement', 'damages', 'liability', 'negligence', 'breach'
        ],
        'property': [
            'property', 'house', 'home', 'apartment', 'building', 'land', 'real estate',
            'mortgage', 'loan', 'foreclosure', 'lease', 'tenant', 'landlord'
        ]
    }
    
    @classmethod
    def _is_preserve_term(cls, word: str) -> bool:
        """Check if a word should be preserved (legal/medical context)"""
        word_lower = word.lower().strip('.,!?')
        for category in cls.PRESERVE_TERMS.values():
            if word_lower in category:
                return True
        return False
    
    @classmethod
    def _is_company_or_title(cls, text: str) -> bool:
        """Check if text appears to be a company name or professional title"""
        company_indicators = ['inc', 'llc', 'corp', 'ltd', 'company', 'co', 'group', 'associates']
        title_indicators = ['dr.', 'mr.', 'ms.', 'mrs.', 'prof.', 'judge', 'attorney']
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in company_indicators + title_indicators)
    
    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Remove PII while preserving legal context
        
        Args:
            text (str): Input text to clean
        
        Returns:
            str: Text with PII removed but legal context preserved
        """
        try:
            cleaned_text = text
            
            # 1. Smart name removal (preserve titles, medical terms, business context)
            def replace_names(match):
                name = match.group(0)
                
                # Don't replace if it contains preserved terms
                words = name.split()
                if any(cls._is_preserve_term(word) for word in words):
                    return name
                
                # Don't replace if it looks like a company or title
                if cls._is_company_or_title(name):
                    return name
                
                # Don't replace if it's at the start of a sentence (might be important)
                if match.start() == 0 or text[match.start()-1] in '.!?':
                    return name
                
                return '[NAME]'
            
            # Match potential names but apply smart filtering
            cleaned_text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', replace_names, cleaned_text)
            
            # 2. Phone numbers (always remove)
            cleaned_text = re.sub(
                r'\b(?:\+\d{1,2}\s?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}\b', 
                '[PHONE]', 
                cleaned_text
            )
            
            # 3. Email addresses (always remove)
            cleaned_text = re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                '[EMAIL]', 
                cleaned_text, 
                flags=re.IGNORECASE
            )
            
            # 4. Social Security Numbers (always remove)
            cleaned_text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', cleaned_text)
            
            # 5. Street addresses (but preserve general locations)
            cleaned_text = re.sub(
                r'\b\d+\s+[A-Z][a-z]+(?: [A-Z][a-z]+)?\s+(Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?)\b', 
                '[ADDRESS]', 
                cleaned_text, 
                flags=re.IGNORECASE
            )
            
            # 6. Credit Card Numbers (always remove)
            cleaned_text = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]', cleaned_text)
            
            # 7. Preserve important dates but remove birthdates/personal dates
            # Only remove dates that look like birthdates (not case-relevant dates)
            def replace_dates(match):
                date = match.group(0)
                # Keep dates that might be relevant to legal cases (recent dates, filing dates, etc.)
                # This is a simple heuristic - you might want to refine this
                return date  # For now, keep all dates as they might be case-relevant
            
            # Comment out aggressive date removal for legal context
            # cleaned_text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', replace_dates, cleaned_text)
            
            # 8. Remove long account numbers but preserve short reference numbers
            cleaned_text = re.sub(r'\b\d{8,}\b', '[ACCOUNT]', cleaned_text)
            
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

    @classmethod
    def test_pii_removal(cls):
        """Test the PII removal with legal case examples"""
        
        test_cases = [
            "My surgeon used a defective medical device during my surgery and it caused complications",
            "My business partner John Smith stole our customer list and started competing",
            "I was fired by ABC Company Inc. for reporting safety violations",
            "Dr. Johnson misdiagnosed my condition at Memorial Hospital",
            "My phone number is 555-123-4567 and email is john@email.com"
        ]
        
        print("🧪 Testing Legal-Context-Aware PII Removal:")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            cleaned = cls.clean_text(test_case)
            original_words = len(test_case.split())
            cleaned_words = len(cleaned.split())
            reduction = ((original_words - cleaned_words) / original_words * 100) if original_words > 0 else 0
            
            print(f"\n{i}. Original ({original_words} words):")
            print(f"   {test_case}")
            print(f"   Cleaned ({cleaned_words} words, {reduction:.1f}% reduction):")
            print(f"   {cleaned}")
            
            # Check if important legal context is preserved
            important_terms = ['surgeon', 'medical device', 'surgery', 'business partner', 'customer list', 'company', 'fired', 'safety violations', 'doctor', 'hospital']
            preserved_terms = [term for term in important_terms if term.lower() in cleaned.lower()]
            
            if preserved_terms:
                print(f"   ✅ Preserved legal context: {', '.join(preserved_terms)}")
            
            if reduction > 40:
                print(f"   ⚠️  High reduction rate: {reduction:.1f}%")
            else:
                print(f"   ✅ Acceptable reduction: {reduction:.1f}%")

if __name__ == "__main__":
    # Run the test
    PIIRemover.test_pii_removal()