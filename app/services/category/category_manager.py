from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CategoryManager:
    """Service for managing legal categories - now unified with CaseAnalyzer"""

    def __init__(self):
        """Initialize CategoryManager with unified categories"""
        # Use same categories as CaseAnalyzer for consistency
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
                "Commercial Real Estate", "Condominiums and Cooperatives", "Construction Disputes",
                "Foreclosures", "Mortgages", "Purchase and Sale of Residence", "Title and Boundary Disputes"
            ],
            "Business/Corporate Law": [
                "Breach of Contract", "Corporate Tax", "Business Disputes", "Buying and Selling a Business",
                "Contract Drafting and Review", "Corporations, LLCs, Partnerships, etc.", "Entertainment Law"
            ],
            "Immigration Law": [
                "Citizenship", "Deportation", "Permanent Visas or Green Cards", "Temporary Visas"
            ],
            "Personal Injury Law": [
                "Automobile Accidents", "Dangerous Property or Buildings", "Defective Products",
                "Medical Malpractice", "Personal Injury (General)"
            ],
            "Wills, Trusts, & Estates Law": [
                "Contested Wills or Probate", "Drafting Wills and Trusts", "Estate Administration", "Estate Planning"
            ],
            "Bankruptcy, Finances, & Tax Law": [
                "Collections", "Consumer Bankruptcy", "Consumer Credit", "Income Tax", "Property Tax"
            ],
            "Government & Administrative Law": [
                "Education and Schools", "Social Security – Disability", "Social Security – Retirement",
                "Social Security – Dependent Benefits", "Social Security – Survivor Benefits", "Veterans Benefits",
                "General Administrative Law", "Environmental Law", "Liquor Licenses", "Constitutional Law"
            ],
            "Product & Services Liability Law": [
                "Attorney Malpractice", "Defective Products", "Warranties", "Consumer Protection and Fraud"
            ],
            "Intellectual Property Law": [
                "Copyright", "Patents", "Trademarks"
            ],
            "Landlord/Tenant Law": [
                "General Landlord and Tenant Issues"
            ]
        }

    def get_all_categories(self) -> List[str]:
        """Get list of all main categories"""
        return list(self.categories.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a main category"""
        return self.categories.get(category, [])

    def validate_category(self, category: str, subcategory: str) -> bool:
        """Validate if category and subcategory combination exists"""
        if category not in self.categories:
            return False
        return subcategory in self.categories[category]

    def get_category_metadata(self, category: str) -> Dict:
        """Get metadata for a category"""
        return {
            "name": category,
            "subcategories": self.get_subcategories(category),
            "total_subcategories": len(self.get_subcategories(category))
        }

    def format_category_name(self, category: str) -> str:
        """Format category name for consistency"""
        return category.strip().replace('EXACTLY', '').strip("'")
    
    def get_all_subcategories(self) -> List[str]:
        """Get all subcategories across all categories"""
        all_subs = []
        for subs in self.categories.values():
            all_subs.extend(subs)
        return all_subs