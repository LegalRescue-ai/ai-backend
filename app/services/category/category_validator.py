from typing import List, Dict, Any, Optional, Union
import re
import logging
from enum import Enum, auto

class ValidationSeverity(Enum):
    """Severity levels for category validation"""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class CategoryManager:
    """Service for managing legal categories and their relationships"""

    def __init__(self):
        """Initialize CategoryManager with categories and their relationships"""
        # Comprehensive categories with all 13 legal categories
        self.categories = {
            "Family Law": [
                "Adoptions", "Child Custody & Visitation", "Child Support",
                "Divorce", "Guardianship", "Paternity", "Separations",
                "Spousal Support or Alimony"
            ],
            "Employment Law": [
                "Disabilities", "Employment Contracts", "Employment Discrimination", 
                "Pensions and Benefits", "Sexual Harassment", "Wages and Overtime Pay", 
                "Workplace Disputes", "Wrongful Termination"
            ],
            "Criminal Law": [
                "General Criminal Defense", "Environmental Violations", "Drug Crimes",
                "Drunk Driving/DUI/DWI", "Felonies", "Misdemeanors",
                "Speeding and Moving Violations", "White Collar Crime", "Tax Evasion"
            ],
            "Real Estate Law": [
                "Commercial Real Estate", "Condominiums and Cooperatives", 
                "Construction Disputes", "Foreclosures", "Mortgages", 
                "Purchase and Sale of Residence", "Title and Boundary Disputes"
            ],
            "Business/Corporate Law": [
                "Breach of Contract", "Corporate Tax", "Business Disputes", 
                "Buying and Selling a Business", "Contract Drafting and Review", 
                "Corporations, LLCs, Partnerships, etc.", "Entertainment Law"
            ],
            "Immigration Law": [
                "Citizenship", "Deportation", 
                "Permanent Visas or Green Cards", "Temporary Visas"
            ],
            "Personal Injury Law": [
                "Automobile Accidents", "Dangerous Property or Buildings", 
                "Defective Products", "Medical Malpractice", "Personal Injury (General)"
            ],
            "Wills, Trusts, & Estates Law": [
                "Contested Wills or Probate", "Drafting Wills and Trusts", 
                "Estate Administration", "Estate Planning"
            ],
            "Bankruptcy, Finances, & Tax Law": [
                "Collections", "Consumer Bankruptcy", "Consumer Credit", 
                "Income Tax", "Property Tax"
            ],
            "Government & Administrative Law": [
                "Education and Schools", "Social Security – Disability", 
                "Social Security – Retirement", "Social Security – Dependent Benefits", 
                "Social Security – Survivor Benefits", "Veterans Benefits", 
                "General Administrative Law", "Environmental Law", 
                "Liquor Licenses", "Constitutional Law"
            ],
            "Product & Services Liability Law": [
                "Attorney Malpractice", "Defective Products", 
                "Warranties", "Consumer Protection and Fraud"
            ],
            "Intellectual Property Law": [
                "Copyright", "Patents", "Trademarks"
            ],
            "Landlord/Tenant Law": [
                "Leases", "Evictions", "Property Repairs"
            ]
        }

        # Comprehensive category keywords
        self.category_keywords = {
    "Family Law": {
        "keywords": [
            "custody", "divorce", "marriage", "child", "support",
            "adoption", "visitation", "spouse", "separation", "alimony",
            "guardianship", "paternity", "matrimonial", "parental rights",
            "child welfare", "family court", "domestic relations"
        ]
    },
    "Employment Law": {
        "keywords": [
            "workplace", "job", "employment", "contract", "discrimination",
            "harassment", "wages", "overtime", "benefits", "termination",
            "worker rights", "employer", "employee", "labor", "wrongful dismissal",
            "workplace safety", "equal opportunity", "minimum wage", "union"
        ]
    },
    "Criminal Law": {
        "keywords": [
            "arrest", "criminal", "felony", "misdemeanor", "dui",
            "drugs", "driving", "police", "charge", "prosecution",
            "defense", "warrant", "conviction", "sentence", "probation",
            "bail", "trial", "legal defense", "criminal record", "indictment"
        ]
    },
    "Real Estate Law": {
        "keywords": [
            "property", "real estate", "mortgage", "foreclosure",
            "landlord", "tenant", "lease", "construction", "title",
            "deed", "zoning", "boundary", "closing", "purchase",
            "commercial property", "residential property", "easement", 
            "property dispute", "property transfer"
        ]
    },
    "Business/Corporate Law": {
        "keywords": [
            "business", "contract", "corporation", "llc", "partnership",
            "breach", "corporate", "shareholder", "merger", "acquisition",
            "startup", "incorporation", "bylaws", "operating agreement",
            "business formation", "corporate governance", "securities", 
            "intellectual property", "compliance", "liability"
        ]
    },
    "Immigration Law": {
        "keywords": [
            "immigration", "visa", "citizenship", "deportation", "green card",
            "naturalization", "alien", "passport", "USCIS", "border",
            "permanent residency", "work permit", "asylum", "refugee",
            "immigration status", "visa application", "entry permit"
        ]
    },
    "Personal Injury Law": {
        "keywords": [
            "injury", "accident", "negligence", "malpractice", "damages",
            "liability", "compensation", "wrongful death", "insurance claim",
            "medical injury", "workplace accident", "product liability",
            "pain and suffering", "medical expenses", "lost wages"
        ]
    },
    "Wills, Trusts, & Estates Law": {
        "keywords": [
            "will", "trust", "estate", "probate", "inheritance",
            "beneficiary", "executor", "testament", "living trust",
            "estate planning", "asset protection", "power of attorney",
            "estate tax", "wealth transfer", "guardianship", "estate administration"
        ]
    },
    "Bankruptcy, Finances, & Tax Law": {
        "keywords": [
            "bankruptcy", "debt", "tax", "credit", "irs",
            "collection", "chapter 7", "chapter 13", "foreclosure",
            "debt relief", "tax audit", "tax liens", "financial restructuring",
            "creditor rights", "debt negotiation", "tax planning"
        ]
    },
    "Government & Administrative Law": {
        "keywords": [
            "government", "administrative", "social security", "disability",
            "benefits", "veterans", "environmental", "education", "constitutional",
            "regulatory compliance", "government agency", "administrative hearing",
            "civil rights", "public policy", "administrative procedure"
        ]
    },
    "Product & Services Liability Law": {
        "keywords": [
            "product liability", "defective", "warranty", "consumer protection",
            "fraud", "malpractice", "negligence", "damages",
            "product safety", "manufacturing defect", "design defect",
            "warning label", "consumer rights", "breach of warranty"
        ]
    },
    "Intellectual Property Law": {
        "keywords": [
            "intellectual property", "copyright", "patent", "trademark",
            "infringement", "licensing", "ip", "invention", "brand",
            "trade secret", "intellectual asset", "royalties", 
            "creative work", "patent protection", "trademark registration"
        ]
    },
    "Landlord/Tenant Law": {
        "keywords": [
            "landlord", "tenant", "lease", "eviction", "rent",
            "security deposit", "repairs", "maintenance", "rental",
            "property management", "lease agreement", "rental dispute",
            "housing rights", "property condition", "rental property"
        ]
    }
}
    def get_all_categories(self) -> List[str]:
        """Get list of all main categories"""
        return list(self.categories.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a main category"""
        return self.categories.get(category, [])

    def format_category_name(self, category: str) -> str:
        """Format category name for consistency"""
        return category.strip().replace('EXACTLY', '').strip("'").strip()

    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a category"""
        return self.category_keywords.get(category, {}).get("keywords", [])

    def get_category_metadata(self, category: str) -> Dict:
        """Get metadata for a category"""
        category = self.format_category_name(category)
        return {
            "name": category,
            "subcategories": self.get_subcategories(category),
            "keywords": self.get_category_keywords(category)
        }

class CategoryValidator:
    """
    Advanced validation utility for legal categories and subcategories
    """

    def __init__(self, category_manager=None):
        """
        Initialize CategoryValidator 
        
        Args:
            category_manager (CategoryManager, optional): Instance of CategoryManager
        """
        self.category_manager = category_manager or CategoryManager()
        self.logger = logging.getLogger(__name__)

    def validate_category(self, category: str, subcategory: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive validation of category and optional subcategory
        
        Args:
            category (str): Main category to validate
            subcategory (Optional[str]): Specific subcategory to validate
        
        Returns:
            Dict with validation results
        """
        validation_results = {
            "is_valid": True,
            "category": category,
            "subcategory": subcategory,
            "messages": []
        }

        # Normalize category name
        try:
            normalized_category = self.category_manager.format_category_name(category)
        except Exception as e:
            return {
                "is_valid": False,
                "category": category,
                "subcategory": subcategory,
                "messages": [{
                    "type": ValidationSeverity.ERROR,
                    "message": f"Invalid category format: {str(e)}"
                }]
            }

        # Check if category exists
        if normalized_category not in self.category_manager.categories:
            validation_results.update({
                "is_valid": False,
                "messages": [{
                    "type": ValidationSeverity.ERROR,
                    "message": f"Category '{normalized_category}' does not exist"
                }]
            })
            return validation_results

        # If subcategory is provided, validate it
        if subcategory:
            normalized_subcategory = subcategory.strip()
            
            if normalized_subcategory not in self.category_manager.categories[normalized_category]:
                validation_results.update({
                    "is_valid": False,
                    "messages": [{
                        "type": ValidationSeverity.ERROR,
                        "message": f"Subcategory '{normalized_subcategory}' does not exist in '{normalized_category}'"
                    }]
                })
            else:
                validation_results["messages"].append({
                    "type": ValidationSeverity.INFO,
                    "message": f"Successfully validated category and subcategory"
                })

        return validation_results

    def analyze_category_compatibility(self, categories: List[str]) -> Dict[str, Any]:
        """
        Analyze compatibility and relationships between multiple categories
        
        Args:
            categories (List[str]): List of categories to analyze
        
        Returns:
            Dict with compatibility analysis
        """
        compatibility_analysis = {
            "input_categories": categories,
            "is_compatible": True,
            "compatibility_score": 100,
            "related_categories": {},
            "messages": []
        }

        # Validate each category
        validated_categories = []
        for category in categories:
            validation = self.validate_category(category)
            if not validation['is_valid']:
                compatibility_analysis['is_compatible'] = False
                compatibility_analysis['messages'].extend(validation['messages'])
            else:
                validated_categories.append(category)

        # Analyze relationships between validated categories
        if validated_categories:
            compatibility_analysis['related_categories'] = self._find_category_relationships(validated_categories)

        # Calculate compatibility score
        if len(validated_categories) != len(categories):
            compatibility_analysis['compatibility_score'] = (len(validated_categories) / len(categories)) * 100

        return compatibility_analysis

    def _find_category_relationships(self, categories: List[str]) -> Dict[str, List[str]]:
        """
        Find potential relationships between categories
        
        Args:
            categories (List[str]): List of categories to analyze
        
        Returns:
            Dict of related categories
        """
        # Predefined category relationships
        category_relationships = {
            "Family Law": ["Employment Law", "Government & Administrative Law"],
            "Employment Law": ["Business/Corporate Law", "Government & Administrative Law"],
            "Criminal Law": ["Personal Injury Law", "Government & Administrative Law"],
            "Real Estate Law": ["Business/Corporate Law", "Bankruptcy, Finances, & Tax Law"],
            "Business/Corporate Law": ["Intellectual Property Law", "Real Estate Law"],
            "Immigration Law": ["Government & Administrative Law"],
            "Personal Injury Law": ["Product & Services Liability Law"],
            "Wills, Trusts, & Estates Law": ["Bankruptcy, Finances, & Tax Law"],
            "Bankruptcy, Finances, & Tax Law": ["Business/Corporate Law"],
            "Government & Administrative Law": ["Constitutional Law"],
            "Product & Services Liability Law": ["Business/Corporate Law"],
            "Intellectual Property Law": ["Business/Corporate Law"],
            "Landlord/Tenant Law": ["Real Estate Law", "Business/Corporate Law"]
        }

        relationships = {}
        for category in categories:
            related = category_relationships.get(category, [])
            relationships[category] = [
                rel for rel in related if rel in categories and rel != category
            ]

        return relationships

    def suggest_alternative_categories(self, input_category: str) -> Dict[str, Any]:
        """
        Suggest alternative or related categories based on an input category
        
        Args:
            input_category (str): Category to find alternatives for
        
        Returns:
            Dict with suggested categories
        """
        # Validate input category
        validation = self.validate_category(input_category)
        if not validation['is_valid']:
            return {
                "input_category": input_category,
                "is_valid": False,
                "suggestions": []
            }

        # Find related categories and all categories
        all_categories = self.category_manager.get_all_categories()
        related_categories = self._find_category_relationships([input_category])[input_category]

        # Prepare suggestions
        suggestions = [
            {
                "category": cat,
                "relationship": "directly related" if cat in related_categories else "potential match",
                "keywords": self.category_manager.get_category_keywords(cat)
            } for cat in all_categories if cat != input_category
        ]

        return {
            "input_category": input_category,
            "is_valid": True,
            "suggestions": suggestions
        }

    def generate_category_report(self, category: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report for a given category
        
        Args:
            category (str): Category to generate report for
        
        Returns:
            Dict with detailed category report
        """
        # Validate category
        validation = self.validate_category(category)
        if not validation['is_valid']:
            return validation

        # Gather category metadata
        metadata = self.category_manager.get_category_metadata(category)

        return {
            "category": category,
            "is_valid": True,
            "metadata": metadata,
            "subcategory_count": len(metadata['subcategories']),
            "keyword_count": len(metadata['keywords']),
            "related_categories": self._find_category_relationships([category]).get(category, [])
        }

def validate_legal_category(category: str, subcategory: Optional[str] = None) -> bool:
    """
    Quick validation utility for external use
    
    Args:
        category (str): Main category to validate
        subcategory (Optional[str]): Specific subcategory to validate
    
    Returns:
        bool: Whether the category (and optional subcategory) is valid
    """
    validator = CategoryValidator()
    result = validator.validate_category(category, subcategory)
    return result['is_valid']