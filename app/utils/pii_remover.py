import re
import logging
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class PIISensitivityLevel(Enum):
    LOW = "low"           # Minimal removal, preserve context
    MEDIUM = "medium"     # Balanced removal
    HIGH = "high"         # Aggressive removal, maximum privacy

@dataclass
class PIIRemovalResult:
    cleaned_text: str
    original_length: int
    cleaned_length: int
    reduction_percentage: float
    pii_found: List[str]
    preserved_terms: List[str]
    warnings: List[str]

class PIIRemover:
    """
    Legal-context-aware PII remover that preserves important case information
    while protecting privacy. Optimized for legal case analysis.
    """
    
    PRESERVE_TERMS = {
        'medical': [
            'doctor', 'dr', 'surgeon', 'physician', 'nurse', 'medical', 'hospital',
            'clinic', 'patient', 'surgery', 'device', 'treatment', 'diagnosis',
            'medication', 'prescription', 'therapy', 'procedure', 'operation',
            'healthcare', 'practitioner', 'specialist', 'radiologist', 'cardiologist',
            'oncologist', 'psychiatrist', 'therapist', 'pharmacist', 'dentist',
            'emergency room', 'er', 'icu', 'operating room', 'or', 'ward', 'unit'
        ],
        'business': [
            'business', 'company', 'corporation', 'llc', 'inc', 'ltd', 'corp',
            'partner', 'partnership', 'customer', 'client', 'vendor', 'supplier',
            'contractor', 'subcontractor', 'employee', 'employer', 'manager',
            'supervisor', 'ceo', 'president', 'director', 'vice president',
            'executive', 'administrator', 'representative', 'agent', 'consultant',
            'freelancer', 'associate', 'colleague', 'coworker', 'staff'
        ],
        'legal': [
            'attorney', 'lawyer', 'counsel', 'solicitor', 'barrister', 'advocate',
            'judge', 'justice', 'magistrate', 'court', 'courthouse', 'tribunal',
            'lawsuit', 'litigation', 'contract', 'agreement', 'settlement',
            'plaintiff', 'defendant', 'respondent', 'petitioner', 'witness',
            'evidence', 'testimony', 'deposition', 'trial', 'hearing', 'proceeding',
            'settlement', 'damages', 'liability', 'negligence', 'breach', 'violation',
            'statute', 'regulation', 'ordinance', 'law', 'legal', 'jurisdiction',
            'federal', 'state', 'local', 'municipal', 'county', 'district'
        ],
        'property': [
            'property', 'real estate', 'house', 'home', 'residence', 'apartment',
            'condo', 'condominium', 'building', 'structure', 'land', 'lot',
            'parcel', 'mortgage', 'loan', 'foreclosure', 'deed', 'title',
            'lease', 'rental', 'tenant', 'landlord', 'lessor', 'lessee',
            'commercial', 'residential', 'industrial', 'zoning', 'easement'
        ],
        'financial': [
            'bank', 'banking', 'credit union', 'financial institution', 'lender',
            'creditor', 'debtor', 'loan', 'mortgage', 'credit', 'debt', 'payment',
            'account', 'checking', 'savings', 'investment', 'insurance', 'policy',
            'premium', 'claim', 'coverage', 'benefits', 'pension', 'retirement',
            'social security', 'disability', 'unemployment', 'workers compensation'
        ],
        'government': [
            'government', 'federal', 'state', 'county', 'city', 'municipal',
            'department', 'agency', 'bureau', 'office', 'administration',
            'commission', 'board', 'authority', 'service', 'center',
            'irs', 'tax', 'social security', 'medicare', 'medicaid', 'va',
            'veterans', 'immigration', 'customs', 'border', 'homeland security',
            'fbi', 'police', 'sheriff', 'officer', 'deputy', 'detective'
        ]
    }
    
    COMPANY_SUFFIXES = [
        'inc', 'incorporated', 'llc', 'corp', 'corporation', 'ltd', 'limited',
        'co', 'company', 'group', 'associates', 'partners', 'partnership',
        'enterprises', 'solutions', 'services', 'systems', 'technologies',
        'consulting', 'holdings', 'international', 'global', 'national',
        'regional', 'local', 'foundation', 'institute', 'organization',
        'association', 'society', 'union', 'guild', 'academy', 'university',
        'college', 'school', 'hospital', 'medical center', 'clinic'
    ]
    
    PROFESSIONAL_TITLES = [
        'dr', 'doctor', 'prof', 'professor', 'mr', 'mrs', 'ms', 'miss',
        'judge', 'justice', 'honorable', 'attorney', 'counselor', 'esq',
        'ceo', 'president', 'vice president', 'director', 'manager',
        'supervisor', 'administrator', 'coordinator', 'specialist',
        'consultant', 'analyst', 'engineer', 'technician', 'nurse',
        'surgeon', 'physician', 'therapist', 'dentist', 'pharmacist'
    ]
    
    def __init__(self, sensitivity_level: PIISensitivityLevel = PIISensitivityLevel.LOW):
        self.sensitivity_level = sensitivity_level
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.phone_patterns = [
            re.compile(r'\b(?:\+\d{1,2}\s?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}\b'),
            re.compile(r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b'),
            re.compile(r'\b\(\d{3}\)\s?\d{3}[\s.-]?\d{4}\b'),
            re.compile(r'\b\+\d{1,3}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}\b')
        ]
        
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        self.ssn_patterns = [
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            re.compile(r'\b\d{3}\s\d{2}\s\d{4}\b')
        ]
        
        self.address_patterns = [
            re.compile(
                r'\b\d+\s+[A-Z][a-z]+(?: [A-Z][a-z]+)?\s+'
                r'(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|'
                r'Lane|Ln\.?|Drive|Dr\.?|Way|Place|Pl\.?|Court|Ct\.?|'
                r'Circle|Cir\.?|Parkway|Pkwy\.?)\b',
                re.IGNORECASE
            )
        ]
        
        self.credit_card_patterns = [
            re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
        ]
        
        self.date_patterns = [
            re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE)
        ]
        
        self.case_number_pattern = re.compile(r'\bCase\s+No\.?\s*\d+[-/]\d+\b', re.IGNORECASE)
        self.bar_number_pattern = re.compile(r'\bBar\s+No\.?\s*\d+\b', re.IGNORECASE)
        self.policy_number_pattern = re.compile(r'\bPolicy\s+No\.?\s*[A-Z0-9-]+\b', re.IGNORECASE)
        self.docket_number_pattern = re.compile(r'\bDocket\s+No\.?\s*\d+[-/]\d+\b', re.IGNORECASE)
        
        self.account_patterns = [
            re.compile(r'\bAccount\s+(?:No\.?|Number)\s*[A-Z0-9-]+\b', re.IGNORECASE),
            re.compile(r'\b\d{10,}\b')
        ]
        
        self.name_pattern = re.compile(
            r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?)?\s+)?[A-Z][a-z]+\b'
        )
        
        self.zip_patterns = [
            re.compile(r'\b\d{5}(?:-\d{4})?\b')
        ]
    
    @classmethod
    def _is_preserve_term(cls, word: str) -> bool:
        word_lower = word.lower().strip('.,!?()[]{}";:')
        for category in cls.PRESERVE_TERMS.values():
            if word_lower in category:
                return True
        return False
    
    @classmethod
    def _is_company_or_title(cls, text: str) -> bool:
        text_lower = text.lower()
        
        for suffix in cls.COMPANY_SUFFIXES:
            if suffix in text_lower:
                return True
        
        for title in cls.PROFESSIONAL_TITLES:
            if text_lower.startswith(title + ' ') or text_lower.startswith(title + '.'):
                return True
        
        return False
    
    def _should_preserve_name(self, name: str, context_before: str = "", context_after: str = "") -> bool:
        words = name.split()
        if any(self._is_preserve_term(word) for word in words):
            return True
        
        if self._is_company_or_title(name):
            return True
        
        context = (context_before + " " + context_after).lower()
        legal_indicators = [
            'attorney', 'lawyer', 'judge', 'court', 'dr.', 'doctor',
            'hospital', 'clinic', 'company', 'corporation', 'inc',
            'vs.', 'v.', 'plaintiff', 'defendant', 'witness'
        ]
        
        if any(indicator in context for indicator in legal_indicators):
            return True
        
        if context_before.strip().endswith('.'):
            return True
        
        if self.sensitivity_level == PIISensitivityLevel.LOW:
            return True
        
        return False
    
    def _should_preserve_date(self, date: str, context: str = "") -> bool:
        context_lower = context.lower()
        
        legal_date_indicators = [
            'filed', 'served', 'occurred', 'happened', 'incident',
            'accident', 'surgery', 'diagnosis', 'treatment', 'signed',
            'executed', 'terminated', 'fired', 'hired', 'injured',
            'arrested', 'charged', 'convicted', 'sentenced'
        ]
        
        if any(indicator in context_lower for indicator in legal_date_indicators):
            return True
        
        birthdate_indicators = ['born', 'birth', 'dob', 'date of birth', 'age']
        if any(indicator in context_lower for indicator in birthdate_indicators):
            return False
        
        if self.sensitivity_level == PIISensitivityLevel.LOW:
            return True
        
        return False
    
    def clean_text(self, text: str) -> PIIRemovalResult:
        try:
            original_text = text
            cleaned_text = text
            pii_found = []
            preserved_terms = []
            warnings = []
            
            # Remove phone numbers
            for pattern in self.phone_patterns:
                matches = pattern.findall(cleaned_text)
                if matches:
                    pii_found.extend([f"phone:{match}" for match in matches])
                    cleaned_text = pattern.sub('[PHONE]', cleaned_text)
            
            # Remove email addresses
            email_matches = self.email_pattern.findall(cleaned_text)
            if email_matches:
                pii_found.extend([f"email:{match}" for match in email_matches])
                cleaned_text = self.email_pattern.sub('[EMAIL]', cleaned_text)
            
            # Remove SSN
            for pattern in self.ssn_patterns:
                matches = pattern.findall(cleaned_text)
                if matches:
                    pii_found.extend([f"ssn:{match}" for match in matches])
                    cleaned_text = pattern.sub('[SSN]', cleaned_text)
            
            # Remove credit card numbers
            for pattern in self.credit_card_patterns:
                matches = pattern.findall(cleaned_text)
                if matches:
                    pii_found.extend([f"credit_card:{match}" for match in matches])
                    cleaned_text = pattern.sub('[CREDIT_CARD]', cleaned_text)
            
            # Remove addresses
            for pattern in self.address_patterns:
                matches = pattern.findall(cleaned_text)
                if matches:
                    pii_found.extend([f"address:{match}" for match in matches])
                    cleaned_text = pattern.sub('[ADDRESS]', cleaned_text)
            
            # Remove ZIP codes (preserve if in legal context)
            for pattern in self.zip_patterns:
                def replace_zip(match):
                    zip_code = match.group(0)
                    start, end = match.span()
                    context = cleaned_text[max(0, start-50):min(len(cleaned_text), end+50)]
                    if 'court' in context.lower() or 'courthouse' in context.lower():
                        preserved_terms.append(f"zip_preserved:{zip_code}")
                        return zip_code
                    pii_found.append(f"zip:{zip_code}")
                    return '[ZIP]'
                
                cleaned_text = pattern.sub(replace_zip, cleaned_text)
            
            # Legal-specific removals
            case_matches = self.case_number_pattern.findall(cleaned_text)
            if case_matches:
                pii_found.extend([f"case_number:{match}" for match in case_matches])
                cleaned_text = self.case_number_pattern.sub('[CASE_NUMBER]', cleaned_text)
            
            bar_matches = self.bar_number_pattern.findall(cleaned_text)
            if bar_matches:
                pii_found.extend([f"bar_number:{match}" for match in bar_matches])
                cleaned_text = self.bar_number_pattern.sub('[BAR_NUMBER]', cleaned_text)
            
            policy_matches = self.policy_number_pattern.findall(cleaned_text)
            if policy_matches:
                pii_found.extend([f"policy_number:{match}" for match in policy_matches])
                cleaned_text = self.policy_number_pattern.sub('[POLICY_NUMBER]', cleaned_text)
            
            docket_matches = self.docket_number_pattern.findall(cleaned_text)
            if docket_matches:
                pii_found.extend([f"docket_number:{match}" for match in docket_matches])
                cleaned_text = self.docket_number_pattern.sub('[DOCKET_NUMBER]', cleaned_text)
            
            # Account numbers (preserve short reference numbers)
            for pattern in self.account_patterns:
                def replace_account(match):
                    account = match.group(0)
                    if len(account.replace(' ', '').replace('-', '')) < 8:
                        preserved_terms.append(f"account_preserved:{account}")
                        return account
                    pii_found.append(f"account:{account}")
                    return '[ACCOUNT]'
                
                cleaned_text = pattern.sub(replace_account, cleaned_text)
            
            # Smart name removal
            def replace_names(match):
                name = match.group(0)
                start, end = match.span()
                
                context_start = max(0, start - 100)
                context_end = min(len(original_text), end + 100)
                context_before = original_text[context_start:start]
                context_after = original_text[end:context_end]
                
                if self._should_preserve_name(name, context_before, context_after):
                    preserved_terms.append(f"name_preserved:{name}")
                    return name
                
                pii_found.append(f"name:{name}")
                return '[NAME]'
            
            cleaned_text = self.name_pattern.sub(replace_names, cleaned_text)
            
            # Smart date removal (only for birthdate-like contexts in MEDIUM/HIGH sensitivity)
            if self.sensitivity_level != PIISensitivityLevel.LOW:
                for pattern in self.date_patterns:
                    def replace_date(match):
                        date = match.group(0)
                        start, end = match.span()
                        context = cleaned_text[max(0, start-50):min(len(cleaned_text), end+50)]
                        
                        if self._should_preserve_date(date, context):
                            preserved_terms.append(f"date_preserved:{date}")
                            return date
                        
                        pii_found.append(f"date:{date}")
                        return '[DATE]'
                    
                    cleaned_text = pattern.sub(replace_date, cleaned_text)
            
            original_length = len(original_text)
            cleaned_length = len(cleaned_text)
            reduction_percentage = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
            
            if reduction_percentage > 60:
                warnings.append(f"High reduction rate: {reduction_percentage:.1f}%")
            
            if len(pii_found) > 10:
                warnings.append(f"Large amount of PII detected: {len(pii_found)} items")
            
            preserved_legal_terms = [term for term in preserved_terms if any(
                category_term in term.lower() 
                for category in self.PRESERVE_TERMS.values() 
                for category_term in category
            )]
            
            if not preserved_legal_terms and 'legal' in original_text.lower():
                warnings.append("No legal context terms preserved - verify text quality")
            
            return PIIRemovalResult(
                cleaned_text=cleaned_text,
                original_length=original_length,
                cleaned_length=cleaned_length,
                reduction_percentage=reduction_percentage,
                pii_found=pii_found,
                preserved_terms=preserved_terms,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"PII removal error: {e}")
            return PIIRemovalResult(
                cleaned_text=text,
                original_length=len(text),
                cleaned_length=len(text),
                reduction_percentage=0.0,
                pii_found=[],
                preserved_terms=[],
                warnings=[f"PII removal failed: {str(e)}"]
            )
    
    @classmethod
    def clean_text_simple(cls, text: str) -> str:
        remover = cls()
        result = remover.clean_text(text)
        return result.cleaned_text
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        masked_data = {}
        sensitive_keys = [
            'name', 'email', 'phone', 'address', 'ssn', 'social_security',
            'credit_card', 'birthdate', 'birth_date', 'dob', 'account',
            'account_number', 'policy', 'policy_number', 'case_number',
            'bar_number', 'docket_number'
        ]
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str):
                    result = self.clean_text(value)
                    masked_data[key] = result.cleaned_text
                else:
                    masked_data[key] = str(value)
            else:
                masked_data[key] = value
        
        return masked_data
    
    def validate_pii_removal(self, original: str, cleaned: str) -> Dict[str, Any]:
        validation_results = {
            "pii_likely_removed": True,
            "context_preserved": True,
            "issues": [],
            "score": 100
        }
        
        potential_pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),
            (r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b', 'Phone'),
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', 'Credit Card')
        ]
        
        for pattern, pii_type in potential_pii_patterns:
            if re.search(pattern, cleaned):
                validation_results["issues"].append(f"Potential {pii_type} found in cleaned text")
                validation_results["pii_likely_removed"] = False
                validation_results["score"] -= 20
        
        legal_terms = []
        for category in self.PRESERVE_TERMS.values():
            for term in category:
                if term in original.lower() and term in cleaned.lower():
                    legal_terms.append(term)
        
        if legal_terms:
            validation_results["preserved_legal_terms"] = legal_terms
        else:
            original_has_legal = any(
                term in original.lower() 
                for category in self.PRESERVE_TERMS.values() 
                for term in category
            )
            cleaned_has_legal = any(
                term in cleaned.lower() 
                for category in self.PRESERVE_TERMS.values() 
                for term in category
            )
            
            if original_has_legal and not cleaned_has_legal:
                validation_results["context_preserved"] = False
                validation_results["issues"].append("Legal context may have been over-removed")
                validation_results["score"] -= 15
        
        reduction_rate = ((len(original) - len(cleaned)) / len(original) * 100) if len(original) > 0 else 0
        if reduction_rate > 70:
            validation_results["issues"].append(f"High reduction rate: {reduction_rate:.1f}%")
            validation_results["score"] -= 10
        
        return validation_results
    
    @classmethod
    def test_pii_removal(cls, sensitivity_level: PIISensitivityLevel = PIISensitivityLevel.LOW):
        test_cases = [
            {
                "description": "Medical malpractice case",
                "text": "Dr. Johnson at Memorial Hospital used a defective cardiac device during my surgery on 03/15/2023. My phone number is 555-123-4567 and email is patient@email.com. Case No. 2023-CV-1234."
            },
            {
                "description": "Business partnership dispute",
                "text": "My business partner John Smith of ABC Company Inc. stole our customer list and started competing. Our contract was signed on January 15, 2022. Contact me at (555) 987-6543."
            },
            {
                "description": "Employment termination",
                "text": "I was fired by XYZ Corporation on 12/01/2023 for reporting safety violations to OSHA. My employee ID was EMP-123456 and my supervisor was Jane Doe."
            },
            {
                "description": "Personal injury accident",
                "text": "I was injured in a car accident at 123 Main Street on February 28, 2023. The other driver was Robert Williams, insurance policy ABC-123-XYZ. My SSN is 123-45-6789."
            },
            {
                "description": "Family law custody case",
                "text": "Attorney Sarah Brown represents me in custody case 2023-FL-5678. My ex-spouse lives at 456 Oak Avenue with our children. Court hearing scheduled for April 10, 2024."
            }
        ]
        
        remover = cls(sensitivity_level)
        
        print(f"Testing Legal-Context-Aware PII Removal (Sensitivity: {sensitivity_level.value.upper()})")
        print("=" * 80)
        
        total_score = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['description']}:")
            print("-" * 60)
            
            original_text = test_case['text']
            result = remover.clean_text(original_text)
            
            print(f"Original ({result.original_length} chars):")
            print(f"  {original_text}")
            print(f"\nCleaned ({result.cleaned_length} chars, {result.reduction_percentage:.1f}% reduction):")
            print(f"  {result.cleaned_text}")
            
            if result.pii_found:
                print(f"\nPII Removed ({len(result.pii_found)} items):")
                for pii in result.pii_found[:5]:
                    print(f"  - {pii}")
                if len(result.pii_found) > 5:
                    print(f"  - ... and {len(result.pii_found) - 5} more")
            
            if result.preserved_terms:
                print(f"\nContext Preserved ({len(result.preserved_terms)} items):")
                for term in result.preserved_terms[:5]:
                    print(f"  - {term}")
                if len(result.preserved_terms) > 5:
                    print(f"  - ... and {len(result.preserved_terms) - 5} more")
            
            if result.warnings:
                print(f"\nWarnings:")
                for warning in result.warnings:
                    print(f"  - {warning}")
            
            validation = remover.validate_pii_removal(original_text, result.cleaned_text)
            print(f"\nValidation Score: {validation['score']}/100")
            
            if validation['issues']:
                print("  Issues:")
                for issue in validation['issues']:
                    print(f"    - {issue}")
            
            total_score += validation['score']
            print("-" * 60)
        
        average_score = total_score / len(test_cases)
        print(f"\nOverall Performance: {average_score:.1f}/100")
        
        if average_score >= 90:
            print("Excellent PII removal performance")
        elif average_score >= 75:
            print("Good PII removal performance")
        elif average_score >= 60:
            print("Acceptable PII removal performance - consider tuning")
        else:
            print("Poor PII removal performance - needs improvement")

if __name__ == "__main__":
    print("Testing with different sensitivity levels:\n")
    
    for level in PIISensitivityLevel:
        PIIRemover.test_pii_removal(level)
        print("\n" + "="*100 + "\n")