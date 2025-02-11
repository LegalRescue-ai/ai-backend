from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CategoryManager:
    """Service for managing legal categories and their relationships"""

    def __init__(self):
        """Initialize CategoryManager with categories and their relationships"""
        # Initialize category data
        self.categories = {
            "Family Law": [
                "Adoptions", "Child Custody & Visitation", "Child Support",
                "Divorce", "Guardianship", "Paternity", "Separations",
                "Spousal Support or Alimony"
            ],
            "Criminal Law": [
                "General Criminal Defense", "Environmental Violations", "Drug Crimes",
                "Drunk Driving/DUI/DWI", "Felonies", "Misdemeanors",
                "Speeding and Moving Violations", "White Collar Crime", "Tax Evasion"
            ],
            # Add other categories...
        }

        # Initialize category keywords for better prediction
        self.category_keywords = {
            "Family Law": {
                "keywords": [
                    "custody", "divorce", "marriage", "child", "support",
                    "adoption", "visitation", "spouse", "separation", "alimony",
                    "guardianship", "paternity", "matrimonial"
                ]
            },
            "Criminal Law": {
                "keywords": [
                    "arrest", "criminal", "felony", "misdemeanor", "dui",
                    "drugs", "driving", "police", "charge", "prosecution",
                    "defense", "warrant", "conviction", "sentence", "probation"
                ]
            },
            # Add other category keywords...
        }

    def get_all_categories(self) -> List[str]:
        """
        Get list of all main categories
        
        Returns:
            List[str]: List of main category names
        """
        return list(self.categories.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """
        Get subcategories for a main category
        
        Args:
            category (str): Main category name
            
        Returns:
            List[str]: List of subcategories or empty list if category not found
        """
        return self.categories.get(category, [])

    def validate_category(self, category: str, subcategory: str) -> bool:
        """
        Validate if category and subcategory combination exists
        
        Args:
            category (str): Main category name
            subcategory (str): Subcategory name
            
        Returns:
            bool: True if valid combination
        """
        if category not in self.categories:
            return False
        return subcategory in self.categories[category]

    def get_category_keywords(self, category: str) -> List[str]:
        """
        Get keywords associated with a category
        
        Args:
            category (str): Main category name
            
        Returns:
            List[str]: List of keywords or empty list if category not found
        """
        return self.category_keywords.get(category, {}).get("keywords", [])

    def suggest_category(self, text: str) -> Optional[Dict[str, str]]:
        """
        Suggest a category based on text content
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Optional[Dict[str, str]]: Dictionary with suggested category and confidence
                                    or None if no match found
        """
        # Basic keyword matching - could be enhanced with ML/AI
        max_matches = 0
        best_category = None

        text = text.lower()
        
        for category, data in self.category_keywords.items():
            matches = sum(1 for keyword in data["keywords"] if keyword.lower() in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category

        if best_category:
            confidence = "high" if max_matches > 5 else "medium" if max_matches > 2 else "low"
            return {
                "category": best_category,
                "confidence": confidence,
                "match_score": max_matches
            }
        
        return None

    def get_category_metadata(self, category: str) -> Dict:
        """
        Get metadata for a category
        
        Args:
            category (str): Main category name
            
        Returns:
            Dict: Category metadata including subcategories and keywords
        """
        return {
            "name": category,
            "subcategories": self.get_subcategories(category),
            "keywords": self.get_category_keywords(category)
        }

    def format_category_name(self, category: str) -> str:
        """
        Format category name for consistency
        
        Args:
            category (str): Category name to format
            
        Returns:
            str: Formatted category name
        """
        return category.strip().replace('EXACTLY', '').strip("'")