import logging
import re
from typing import List, Dict, Optional, Any

class CategoryPredictor:
    """Predicts the legal category based on input text using predefined keywords."""

    def __init__(self):
        """Initialize the CategoryPredictor with legal categories and associated keywords."""
        self.logger = logging.getLogger(__name__)

        # Legal categories and subcategories
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
                "Citizenship", "Deportation", "Permanent Visas or Green Cards",
                "Temporary Visas"
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

        # Keyword-based matching for category prediction
        self.category_keywords = {
            "Family Law": [
                "custody", "divorce", "marriage", "child", "support",
                "adoption", "visitation", "spouse", "separation", "alimony",
                "guardianship", "paternity", "matrimonial", "family court",
                "domestic relations", "parental rights"
            ],
            "Employment Law": [
                "workplace", "job", "employment", "contract", "discrimination",
                "harassment", "wages", "overtime", "benefits", "termination",
                "employer", "employee", "labor", "wrongful dismissal"
            ],
            "Criminal Law": [
                "arrest", "criminal", "felony", "misdemeanor", "dui",
                "drugs", "driving", "police", "charge", "prosecution",
                "defense", "warrant", "conviction", "sentence", "probation",
                "bail", "trial", "legal defense"
            ],
            "Real Estate Law": [
                "property", "real estate", "mortgage", "foreclosure",
                "landlord", "tenant", "lease", "construction", "title",
                "deed", "zoning", "boundary", "closing", "purchase"
            ],
            "Business/Corporate Law": [
                "business", "contract", "corporation", "llc", "partnership",
                "breach", "corporate", "shareholder", "merger", "acquisition",
                "startup", "incorporation", "business formation", "liability"
            ],
            "Immigration Law": [
                "immigration", "visa", "citizenship", "deportation", "green card",
                "naturalization", "passport", "USCIS", "border", "asylum"
            ]
        }

    def predict_category(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Predict the most likely legal category based on keyword matches.
        
        Args:
            text (str): User-provided legal case description
        
        Returns:
            Dict[str, Any]: Predicted category with confidence level and matched keywords.
        """
        text = text.lower()
        category_scores = {}

        for category, keywords in self.category_keywords.items():
            unique_matches = set(keyword for keyword in keywords if keyword in text)
            score = len(unique_matches)
            category_scores[category] = {"score": score, "matched_keywords": list(unique_matches)}

        # Find the best matching category
        if category_scores:
            best_category = max(category_scores, key=lambda k: category_scores[k]['score'])
            best_score = category_scores[best_category]['score']

            confidence = "low"
            if best_score > 5:
                confidence = "high"
            elif best_score > 2:
                confidence = "medium"

            return {
                "category": best_category,
                "confidence": confidence,
                "match_score": best_score,
                "matched_keywords": category_scores[best_category]['matched_keywords']
            }

        return None

    def get_categories(self) -> List[str]:
        """
        Retrieve the list of main legal categories.

        Returns:
            List[str]: All available legal categories.
        """
        return list(self.categories.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """
        Retrieve subcategories for a given category.

        Args:
            category (str): Main category name.

        Returns:
            List[str]: List of subcategories, or an empty list if not found.
        """
        return self.categories.get(category, [])

def get_legal_prediction(text: str) -> Optional[Dict[str, Any]]:
    """
    Utility function to predict a legal category.

    Args:
        text (str): Input legal case description.

    Returns:
        Optional[Dict[str, Any]]: Predicted category details or None.
    """
    predictor = CategoryPredictor()
    return predictor.predict_category(text)
