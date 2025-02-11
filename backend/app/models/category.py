from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum, auto
import json
import os
import re
import uuid

class CategoryType(Enum):
    """Enum to define types of legal categories"""
    PRIMARY = auto()
    SECONDARY = auto()
    SPECIALIZED = auto()

@dataclass
class SubCategory:
    """Represents a specific subcategory within a legal category"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    complexity_level: int = 1  # 1-5 scale of legal complexity
    forms_available: bool = False
    typical_documents: List[str] = field(default_factory=list)

@dataclass
class LegalCategory:
    """
    Comprehensive representation of a legal category
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    subcategories: List[SubCategory] = field(default_factory=list)
    type: CategoryType = CategoryType.PRIMARY
    related_categories: List[str] = field(default_factory=list)
    code: Optional[str] = None

class CategoryManager:
    """
    Manages legal categories with advanced querying and management capabilities
    """
    
    _CATEGORIES: Dict[str, LegalCategory] = {
        "Family Law": LegalCategory(
            name="Family Law",
            description="Legal matters involving family relationships and domestic issues",
            subcategories=[
                SubCategory(
                    name="Adoptions",
                    keywords=["child adoption", "legal guardianship", "parental rights"],
                    complexity_level=3
                ),
                SubCategory(
                    name="Child Custody & Visitation",
                    keywords=["custody", "visitation rights", "parental access"],
                    complexity_level=4
                ),
                SubCategory(
                    name="Child Support",
                    keywords=["financial support", "child maintenance", "parental obligations"],
                    complexity_level=3
                ),
                SubCategory(
                    name="Divorce",
                    keywords=["marriage dissolution", "asset division", "spousal support"],
                    complexity_level=4
                ),
                SubCategory(
                    name="Guardianship",
                    keywords=["legal protection", "ward management", "incapacity"],
                    complexity_level=3
                ),
                SubCategory(
                    name="Paternity",
                    keywords=["father's rights", "biological parent", "legal recognition"],
                    complexity_level=2
                ),
                SubCategory(
                    name="Separations",
                    keywords=["legal separation", "living apart", "marriage status"],
                    complexity_level=3
                ),
                SubCategory(
                    name="Spousal Support or Alimony",
                    keywords=["financial support", "maintenance", "post-divorce"],
                    complexity_level=3
                )
            ]
        ),
        "Employment Law": LegalCategory(
            name="Employment Law",
            description="Legal issues related to workplace rights and employment relationships",
            subcategories=[
                SubCategory(name="Disabilities", keywords=["workplace accommodation", "ADA", "discrimination"]),
                SubCategory(name="Employment Contracts", keywords=["job agreement", "terms of employment", "contract review"]),
                SubCategory(name="Employment Discrimination", keywords=["workplace bias", "equal opportunity", "civil rights"]),
                SubCategory(name="Pensions and Benefits", keywords=["retirement", "healthcare", "employee compensation"]),
                SubCategory(name="Sexual Harassment", keywords=["workplace misconduct", "hostile environment", "inappropriate behavior"]),
                SubCategory(name="Wages and Overtime Pay", keywords=["compensation", "labor rights", "wage disputes"]),
                SubCategory(name="Workplace Disputes", keywords=["conflict resolution", "grievance", "workplace issues"]),
                SubCategory(name="Wrongful Termination", keywords=["unjust firing", "employment law", "job protection"])
            ]
        ),
        "Criminal Law": LegalCategory(
            name="Criminal Law",
            description="Legal matters involving criminal offenses and defense",
            subcategories=[
                SubCategory(name="General Criminal Defense", keywords=["legal defense", "criminal charges", "court representation"]),
                SubCategory(name="Environmental Violations", keywords=["environmental crime", "regulatory compliance", "ecological law"]),
                SubCategory(name="Drug Crimes", keywords=["substance offenses", "possession", "distribution"]),
                SubCategory(name="Drunk Driving/DUI/DWI", keywords=["traffic offense", "alcohol-related crime", "license suspension"]),
                SubCategory(name="Felonies", keywords=["serious crime", "criminal prosecution", "serious legal consequences"]),
                SubCategory(name="Misdemeanors", keywords=["minor offenses", "criminal charges", "legal penalties"]),
                SubCategory(name="Speeding and Moving Violations", keywords=["traffic law", "driving infractions", "legal penalties"]),
                SubCategory(name="White Collar Crime", keywords=["financial fraud", "corporate crime", "non-violent offenses"]),
                SubCategory(name="Tax Evasion", keywords=["tax fraud", "financial crime", "IRS violations"])
            ]
        ),
        "Real Estate Law": LegalCategory(
            name="Real Estate Law",
            description="Legal matters involving property, ownership, and real estate transactions",
            subcategories=[
                SubCategory(name="Commercial Real Estate", keywords=["business property", "commercial transactions", "lease agreements"]),
                SubCategory(name="Condominiums and Cooperatives", keywords=["property ownership", "shared spaces", "HOA"]),
                SubCategory(name="Construction Disputes", keywords=["building contracts", "construction law", "project conflicts"]),
                SubCategory(name="Foreclosures", keywords=["property seizure", "mortgage default", "bank proceedings"]),
                SubCategory(name="Mortgages", keywords=["home loans", "property financing", "lending"]),
                SubCategory(name="Purchase and Sale of Residence", keywords=["real estate transaction", "property transfer", "home buying"]),
                SubCategory(name="Title and Boundary Disputes", keywords=["property lines", "ownership conflicts", "land rights"])
            ]
        ),
        "Business/Corporate Law": LegalCategory(
            name="Business/Corporate Law",
            description="Legal matters involving business operations, transactions, and corporate governance",
            subcategories=[
                SubCategory(name="Breach of Contract", keywords=["contract violation", "legal dispute", "business agreement"]),
                SubCategory(name="Corporate Tax", keywords=["business taxation", "financial compliance", "tax strategy"]),
                SubCategory(name="Business Disputes", keywords=["conflict resolution", "corporate litigation", "business conflicts"]),
                SubCategory(name="Buying and Selling a Business", keywords=["business transfer", "acquisition", "sale negotiation"]),
                SubCategory(name="Contract Drafting and Review", keywords=["legal documentation", "agreement preparation", "contract analysis"]),
                SubCategory(name="Corporations, LLCs, Partnerships, etc.", keywords=["business structure", "legal entity", "corporate formation"]),
                SubCategory(name="Entertainment Law", keywords=["media rights", "intellectual property", "creative industry"])
            ]
        ),
        "Immigration Law": LegalCategory(
            name="Immigration Law",
            description="Legal matters involving citizenship, visas, and immigration status",
            subcategories=[
                SubCategory(name="Citizenship", keywords=["naturalization", "legal residency", "citizenship application"]),
                SubCategory(name="Deportation", keywords=["removal proceedings", "immigration enforcement", "legal status"]),
                SubCategory(name="Permanent Visas or Green Cards", keywords=["permanent residency", "immigration status", "work authorization"]),
                SubCategory(name="Temporary Visas", keywords=["short-term stay", "travel authorization", "visa types"])
            ]
        ),
        "Personal Injury Law": LegalCategory(
            name="Personal Injury Law",
            description="Legal matters involving physical or psychological harm caused by others",
            subcategories=[
                SubCategory(name="Automobile Accidents", keywords=["car crash", "vehicle injury", "insurance claim"]),
                SubCategory(name="Dangerous Property or Buildings", keywords=["premises liability", "property hazards", "unsafe conditions"]),
                SubCategory(name="Defective Products", keywords=["product liability", "manufacturing defect", "consumer protection"]),
                SubCategory(name="Medical Malpractice", keywords=["medical negligence", "healthcare error", "professional misconduct"]),
                SubCategory(name="Personal Injury (General)", keywords=["bodily harm", "compensation", "injury claim"])
            ]
        ),
        "Wills, Trusts, & Estates Law": LegalCategory(
            name="Wills, Trusts, & Estates Law",
            description="Legal matters involving estate planning, inheritance, and asset distribution",
            subcategories=[
                SubCategory(name="Contested Wills or Probate", keywords=["inheritance dispute", "estate litigation", "will challenge"]),
                SubCategory(name="Drafting Wills and Trusts", keywords=["estate planning", "asset protection", "legal documentation"]),
                SubCategory(name="Estate Administration", keywords=["estate management", "asset distribution", "executor duties"]),
                SubCategory(name="Estate Planning", keywords=["future planning", "asset preservation", "inheritance strategy"])
            ]
        ),
        "Bankruptcy, Finances, & Tax Law": LegalCategory(
            name="Bankruptcy, Finances, & Tax Law",
            description="Legal matters involving financial difficulties, debt relief, and taxation",
            subcategories=[
                SubCategory(name="Collections", keywords=["debt recovery", "creditor rights", "financial collection"]),
                SubCategory(name="Consumer Bankruptcy", keywords=["debt relief", "financial restructuring", "Chapter 7/13"]),
                SubCategory(name="Consumer Credit", keywords=["credit rights", "lending regulations", "financial protection"]),
                SubCategory(name="Income Tax", keywords=["tax obligations", "IRS compliance", "tax planning"]),
                SubCategory(name="Property Tax", keywords=["real estate taxation", "local government levy", "tax assessment"])
            ]
        ),
        "Government & Administrative Law": LegalCategory(
            name="Government & Administrative Law",
            description="Legal matters involving government regulations, benefits, and administrative processes",
            subcategories=[
                SubCategory(name="Education and Schools", keywords=["educational rights", "school law", "student protection"]),
                SubCategory(name="Social Security – Disability", keywords=["disability benefits", "SSI", "medical evaluation"]),
                SubCategory(name="Social Security – Retirement", keywords=["retirement benefits", "pension", "senior rights"]),
                SubCategory(name="Social Security – Dependent Benefits", keywords=["family benefits", "dependent support", "social security"]),
                SubCategory(name="Social Security – Survivor Benefits", keywords=["death benefits", "family support", "survivor rights"]),
                SubCategory(name="Veterans Benefits", keywords=["military benefits", "veteran support", "service-related compensation"]),
                SubCategory(name="General Administrative Law", keywords=["government regulations", "administrative procedures", "citizen rights"]),
                SubCategory(name="Environmental Law", keywords=["ecological regulations", "conservation", "environmental protection"]),
                SubCategory(name="Liquor Licenses", keywords=["alcohol sales", "regulatory compliance", "business licensing"]),
                SubCategory(name="Constitutional Law", keywords=["fundamental rights", "legal interpretation", "constitutional protections"])
            ]
        ),
        "Product & Services Liability Law": LegalCategory(
            name="Product & Services Liability Law",
            description="Legal matters involving product safety, warranties, and consumer protection",
            subcategories=[
                SubCategory(name="Attorney Malpractice", keywords=["legal negligence", "professional misconduct", "legal error"]),
                SubCategory(name="Defective Products", keywords=["product safety", "manufacturing defect", "consumer protection"]),
                SubCategory(name="Warranties", keywords=["product guarantee", "service agreement", "consumer rights"]),
                SubCategory(name="Consumer Protection and Fraud", keywords=["deceptive practices", "consumer rights", "legal remedy"])
            ]
        ),
        "Intellectual Property Law": LegalCategory(
            name="Intellectual Property Law",
            description="Legal matters involving creative works, inventions, and intellectual assets",
            subcategories=[
                SubCategory(name="Copyright", keywords=["creative rights", "intellectual protection", "artistic ownership"]),
                SubCategory(name="Patents", keywords=["invention protection", "technological innovation", "intellectual asset"]),
                SubCategory(name="Trademarks", keywords=["brand protection", "business identity", "commercial symbol"])
            ]
        ),
        "Landlord/Tenant Law": LegalCategory(
            name="Landlord/Tenant Law",
            description="Legal matters involving rental properties, tenant rights, and housing regulations",
            subcategories=[
                SubCategory(name="Leases", keywords=["rental agreement", "contract terms", "housing lease"]),
                SubCategory(name="Evictions", keywords=["property repossession", "tenant removal", "legal notice"]),
                SubCategory(name="Property Repairs", keywords=["maintenance obligations", "habitability", "property condition"])
            ]
        )
    }

    @classmethod
    def get_category(cls, category_name: str) -> Optional[LegalCategory]:
        """
        Retrieve a specific legal category
        
        Args:
            category_name (str): Name of the category
        
        Returns:
            Optional[LegalCategory]: Category if found, None otherwise
        """
        # Normalize category name (case-insensitive, trim whitespace)
        normalized_name = category_name.strip().title()
        return cls._CATEGORIES.get(normalized_name)

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """
        Get names of all available categories
        
        Returns:
            List[str]: List of category names
        """
        return list(cls._CATEGORIES.keys())

    @classmethod
    def get_subcategories(cls, category_name: str) -> List[SubCategory]:
        """
        Get subcategories for a specific category
        
        Args:
            category_name (str): Name of the category
        
        Returns:
            List[SubCategory]: List of subcategories
        """
        category = cls.get_category(category_name)
        return category.subcategories if category else []

    @classmethod
    def search_categories(cls, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search categories and subcategories based on a query
        
        Args:
            query (str): Search term
            limit (int): Maximum number of results
        
        Returns:
            List[Dict[str, Any]]: Matching categories and subcategories
        """
        results = []
        query = query.lower()

        for category_name, category in cls._CATEGORIES.items():
            # Check category name and description
            if (query in category_name.lower() or 
                (category.description and query in category.description.lower())):
                results.append({
                    "name": category_name,
                    "type": "category",
                    "match_type": "name" if query in category_name.lower() else "description"
                })

            # Check subcategories
            for subcategory in category.subcategories:
                if (query in subcategory.name.lower() or 
                    any(query in keyword.lower() for keyword in subcategory.keywords)):
                    results.append({
                        "name": subcategory.name,
                        "category": category_name,
                        "type": "subcategory",
                        "match_type": "name" if query in subcategory.name.lower() else "keyword"
                    })

            # Stop if limit is reached
            if len(results) >= limit:
                break

        return results[:limit]

    @classmethod
    def validate_category(cls, category_name: str, subcategory_name: Optional[str] = None) -> bool:
        """
        Validate if a category (and optional subcategory) exists
        
        Args:
            category_name (str): Name of the category
            subcategory_name (Optional[str]): Name of the subcategory
        
        Returns:
            bool: True if valid, False otherwise
            """
        # Normalize category and subcategory names
        normalized_category = category_name.strip().title()
        normalized_subcategory = subcategory_name.strip().title() if subcategory_name else None

        # Check if category exists
        category = cls.get_category(normalized_category)
        if not category:
            return False
        
        # If subcategory is specified, check its existence
        if normalized_subcategory:
            return any(sub.name == normalized_subcategory for sub in category.subcategories)
        
        return True

    @classmethod
    def get_category_complexity(cls, category_name: str) -> Dict[str, Any]:
        """
        Calculate and return complexity details for a category
        
        Args:
            category_name (str): Name of the category
        
        Returns:
            Dict with complexity metrics
        """
        category = cls.get_category(category_name)
        if not category:
            return {}

        subcategory_complexities = [sub.complexity_level for sub in category.subcategories]
        
        return {
            "category": category_name,
            "average_complexity": sum(subcategory_complexities) / len(subcategory_complexities),
            "max_complexity": max(subcategory_complexities),
            "min_complexity": min(subcategory_complexities),
            "subcategory_count": len(category.subcategories)
        }

    @classmethod
    def find_related_categories(cls, category_name: str) -> List[str]:
        """
        Find categories related to the given category
        
        Args:
            category_name (str): Name of the category
        
        Returns:
            List of related category names
        """
        related_mapping = {
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

        return related_mapping.get(category_name, [])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entire category management system to a dictionary
        
        Returns:
            Dict[str, Any]: Serialized categories
        """
        return {
            name: {
                "name": category.name,
                "description": category.description,
                "type": category.type.name,
                "subcategories": [
                    {
                        "name": sub.name,
                        "description": sub.description,
                        "keywords": sub.keywords,
                        "complexity_level": sub.complexity_level
                    } for sub in category.subcategories
                ]
            } for name, category in self._CATEGORIES.items()
        }

    @classmethod
    def get_categories_by_type(cls, category_type: CategoryType) -> List[str]:
        """
        Get categories of a specific type
        
        Args:
            category_type (CategoryType): Type of category
        
        Returns:
            List of category names matching the type
        """
        return [
            name for name, category in cls._CATEGORIES.items() 
            if category.type == category_type
        ]

    @classmethod
    def export_categories_to_json(cls, file_path: str):
        """
        Export categories to a JSON file
        
        Args:
            file_path (str): Path to save the JSON file
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(cls().to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting categories: {e}")
            return False

    @classmethod
    def import_categories_from_json(cls, file_path: str):
        """
        Import categories from a JSON file
        
        Args:
            file_path (str): Path to the JSON file
        """
        try:
            with open(file_path, 'r') as f:
                categories_data = json.load(f)
            
            # Clear existing categories
            cls._CATEGORIES.clear()
            
            # Rebuild categories
            for category_name, category_info in categories_data.items():
                subcategories = [
                    SubCategory(
                        name=sub['name'],
                        description=sub.get('description'),
                        keywords=sub.get('keywords', []),
                        complexity_level=sub.get('complexity_level', 1)
                    ) for sub in category_info.get('subcategories', [])
                ]
                
                cls._CATEGORIES[category_name] = LegalCategory(
                    name=category_name,
                    description=category_info.get('description'),
                    subcategories=subcategories,
                    type=CategoryType[category_info.get('type', 'PRIMARY')]
                )
            
            return True
        except Exception as e:
            print(f"Error importing categories: {e}")
            return False

# Optional: Preload categories when the module is imported
CategoryManager.initialize_categories()