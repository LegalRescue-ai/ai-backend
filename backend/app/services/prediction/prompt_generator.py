import logging
from typing import Dict, Any, Optional


class PromptGenerator:
    """
    Generates structured AI prompts based on legal categories and subcategories.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the PromptGenerator with predefined legal categories.

        Args:
            logger (Optional[logging.Logger]): Logger instance for tracking.
        """
        self.logger = logger or logging.getLogger(__name__)

        # Comprehensive legal categories and subcategories
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

    def generate_prompt(self, category: str, subcategory: str) -> str:
        """
        Generates an AI prompt based on the selected legal category and subcategory.

        Args:
            category (str): The main legal category.
            subcategory (str): The specific subcategory.

        Returns:
            str: The structured AI prompt.
        """
        try:
            # Validate category and subcategory
            if category not in self.categories:
                raise ValueError(f"Unsupported category: {category}")

            if subcategory not in self.categories[category]:
                raise ValueError(f"Invalid subcategory for {category}: {subcategory}")

            # Generate a structured legal prompt
            return f"""You are an AI legal assistant helping a lawyer specializing in {category} cases, particularly in {subcategory}.

    **Instructions for AI:**
    - Use professional legal terminology appropriate for {category} cases.
    - DO NOT include any **Personally Identifiable Information (PII)** such as:
        - Names (use placeholders like "the plaintiff" or "the client").
        - Dates (convert into US date formats like MM/DD/YYYY where necessary).
        - Addresses, phone numbers, or emails.
    - Summarize legal case details **without personal details**.
    - Provide AI confidence levels for each classification.
    - Structure responses clearly using **bullet points** and **sections**.

    **Response Format (JSON):**
    {{
      "summary": "Concise legal summary for {subcategory}...",
      "confidence_level": "High/Medium/Low",
      "key_issues_identified": [
        "Issue 1...",
        "Issue 2...",
        "Issue 3..."
      ],
      "suggested_next_steps": [
        "Step 1...",
        "Step 2...",
        "Step 3..."
      ]
    }}
            """
        except Exception as e:
            self.logger.error(f"Error generating prompt: {e}")
            return ""

    def get_legal_questions(self, category: str, subcategory: str) -> Dict[str, Any]:
        """
        Retrieves predefined legal questions for the given category and subcategory.

        Args:
            category (str): The main legal category.
            subcategory (str): The specific subcategory.

        Returns:
            Dict[str, Any]: A dictionary with structured legal questions.
        """
    legal_questions = {
    "Family Law": {
        "Adoptions": [
            "What is your age?",
            "What is your marital status?",
            "What is your relationship to the child?",
            "What is the current custody status of the child?",
            "What is the biological parents' position regarding adoption?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ],
        "Child Custody & Visitation": [
            "What is your age?",
            "What is your relationship with the other parent?",
            "What is the current custody arrangement?",
            "What is your gross annual income?",
            "How many children are involved?",
            "When are you planning to hire an attorney?"
        ],
        "Child Support": [
            "What is your age?",
            "What is your occupation?",
            "How many children are involved?",
            "What is the current child support agreement?",
            "What is your gross annual income?",
            "What is the other parent’s income?",
            "When are you planning to hire an attorney?"
        ],
        "Divorce": [
            "What is your age?",
            "What is your marital status?",
            "Do you have any children?",
            "What are your assets and debts?",
            "What is your spouse’s occupation?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ],
        "Guardianship": [
            "Who are you seeking guardianship for?",
            "What is your relationship to them?",
            "What is their current custody arrangement?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Employment Law": {
        "Disabilities": [
            "What is your occupation?",
            "What is your disability?",
            "Are you still employed?",
            "Has your employer made accommodations?",
            "Have you faced discrimination due to your disability?",
            "When are you planning to hire an attorney?"
        ],
        "Employment Contracts": [
            "What is your occupation?",
            "Do you have a written employment contract?",
            "Are you facing a contract dispute?",
            "What is your employer's industry?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Criminal Law": {
        "General Criminal Defense": [
            "What crime(s) are you accused of?",
            "When were you arrested? (MM/DD/YYYY)",
            "What is your prior criminal history?",
            "Are you currently in custody?",
            "Has bail been set?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ],
        "DUI/DWI": [
            "What was your Blood Alcohol Content (BAC) level?",
            "When were you arrested? (MM/DD/YYYY)",
            "Have you been convicted of a DUI before?",
            "Were you involved in an accident?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Real Estate Law": {
        "Foreclosures": [
            "What is the current market value of the property?",
            "How many months of missed mortgage payments?",
            "Was a foreclosure lawsuit filed?",
            "When are you planning to hire an attorney?"
        ],
        "Title and Boundary Disputes": [
            "What is your role in the dispute?",
            "Who is the dispute with?",
            "What is the estimated value of the property?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Business/Corporate Law": {
        "Breach of Contract": [
            "When was the contract entered into? (MM/DD/YYYY)",
            "What type of contract was it?",
            "What is the approximate value of the contract?",
            "When was the contract breached?",
            "When are you planning to hire an attorney?"
        ],
        "Business Disputes": [
            "What type of business dispute are you facing?",
            "Is there a written contract involved?",
            "What is the approximate financial value of the dispute?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Immigration Law": {
        "Citizenship": [
            "What is your current immigration status?",
            "Have you lived in the U.S. as a lawful resident for at least 5 years?",
            "Have you been outside the U.S. for more than a year in the last 5 years?",
            "Do you meet the good moral character requirement?",
            "When are you planning to hire an attorney?"
        ],
        "Deportation": [
            "What is your immigration status?",
            "Is there a deportation hearing scheduled?",
            "Why is deportation being pursued?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Personal Injury Law": {
        "Automobile Accidents": [
            "When did the accident occur? (MM/DD/YYYY)",
            "What injuries were sustained?",
            "Was a police report filed?",
            "Who was found at fault?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ],
        "Medical Malpractice": [
            "What type of malpractice occurred?",
            "When did you receive the medical treatment? (MM/DD/YYYY)",
            "What injuries or complications did you suffer?",
            "When did you first discover the malpractice?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Wills, Trusts, & Estates Law": {
        "Drafting Wills and Trusts": [
            "What is the estimated value of your estate?",
            "Who will be the beneficiaries?",
            "Do you already have a will or trust?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Bankruptcy, Finances, & Tax Law": {
        "Consumer Bankruptcy": [
            "What is your marital status?",
            "Why do you want to file for bankruptcy?",
            "What debts do you owe?",
            "Have you filed for bankruptcy before?",
            "What is your gross annual income?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Government & Administrative Law": {
        "Veterans Benefits": [
            "What branch of the armed forces did you serve in?",
            "What are your dates of service?",
            "What is your disability or injury?",
            "Have you applied for veterans' benefits?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Product & Services Liability Law": {
        "Defective Products": [
            "When was the product purchased? (MM/DD/YYYY)",
            "What was the cost of the product?",
            "What injuries did the product cause?",
            "Who was the product purchased from?",
            "When are you planning to hire an attorney?"
        ]
    },
    "Intellectual Property Law": {
        "Copyright": [
            "Why are you seeking legal assistance?",
            "What is the subject matter of the copyrighted work?",
            "Who is the dispute with (if applicable)?",
            "When are you planning to hire an attorney?"
        ],
        "Patents": [
            "Why are you seeking legal assistance?",
            "What stage is the invention currently in?",
            "When was the invention completed? (MM/DD/YYYY)",
            "When are you planning to hire an attorney?"
        ]
    },
    "Landlord/Tenant Law": {
        "Leases": [
            "What is your role in this matter?",
            "When did the tenant move into the property? (MM/DD/YYYY)",
            "What type of rental agreement exists?",
            "What is the tenant's current status?",
            "When are you planning to hire an attorney?"
        ],
        "Evictions": [
            "Has an eviction notice been served?",
            "What is the reason for eviction?",
            "What is the current status of the case?",
            "When are you planning to hire an attorney?"
        ]
    }
}

def generate_prompt(self, category, subcategory):
        """
        Generates a prompt based on the selected category and subcategory.
        
        Args:
            category (str): The legal category.
            subcategory (str): The legal subcategory.
        
        Returns:
            str: Generated prompt.
        """
        if category in self.legal_questions and subcategory in self.legal_questions[category]:
            return f"Generate a detailed legal response for {subcategory} under {category}. Provide relevant legal insights."
        else:
            return "Invalid category or subcategory."

def get_legal_questions(self, category, subcategory):
        """
        Retrieves legal questions for the given category and subcategory.

        Args:
            category (str): The legal category.
            subcategory (str): The legal subcategory.

        Returns:
            dict: Category, subcategory, and related legal questions.
        """
        if category in self.legal_questions and subcategory in self.legal_questions[category]:
            return {
                "category": category,
                "subcategory": subcategory,
                "questions": self.legal_questions[category][subcategory]
            }
        else:
            return {"error": "No predefined questions available for this category/subcategory."}


# Example Usage
if __name__ == "__main__":
    generator = PromptGenerator()
    
    category = "Criminal Law"
    subcategory = "General Criminal Defense"

    # Generate prompt
    prompt = generator.generate_prompt(category, subcategory)
    print("\nGenerated AI Prompt:\n", prompt)

    # Retrieve legal questions
    questions = generator.get_legal_questions(category, subcategory)
    print("\nLegal Questions:\n", questions)