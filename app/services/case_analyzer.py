from typing import Dict, Any
import openai
from datetime import datetime
import json

from app.utils.pii_remover import PIIRemover


class CaseAnalyzer:
    """Service for analyzing legal cases using GPT-4o"""

    LEGAL_CATEGORIES = {
        "Family Law": [
            "Adoptions", "Child Custody & Visitation", "Child Support", "Divorce",
            "Guardianship", "Paternity", "Separations", "Spousal Support or Alimony"
        ],
        "Employment Law": [
            "Disabilities", "Employment Contracts", "Employment Discrimination", "Pensions and Benefits",
            "Sexual Harassment", "Wages and Overtime Pay", "Workplace Disputes", "Wrongful Termination"
        ],
        "Criminal Law": [
            "General Criminal Defense", "Environmental Violations", "Drug Crimes", "Drunk Driving/DUI/DWI",
            "Felonies", "Misdemeanors", "Speeding and Moving Violations", "White Collar Crime", "Tax Evasion"
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
        "Landlord/Tenant Law": []
    }

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.pii_remover = PIIRemover()

    def initial_analysis(self, case_text: str) -> Dict[str, Any]:
        """
        Perform initial case analysis to classify the legal case and extract key details.
        
        Args:
            case_text (str): Raw case text from user.
        
        Returns:
            Dict containing analysis results.
        """
        try:
            cleaned_text = self.pii_remover.clean_text(case_text)

            # Create GPT-4o prompt for classification
            prompt = f"""Analyze this legal case and:
            1. Categorize the case into one of the 13 legal categories and select the correct subcategory.
               - Available categories and subcategories:
               {self.LEGAL_CATEGORIES}

            2. Provide a confidence level (high/medium/low).
            3. Generate a specific case title (maximum 70 characters) that describes key aspects WITHOUT any PII.
            4. Extract key case details relevant for legal forms.

            Respond in JSON format:
                
                
           
            {{
                "category": "Selected category",
                "subcategory": "Selected subcategory",
                "confidence": "high/medium/low",
                "key_details": "List of relevant case details"
            }}

            Case details: {cleaned_text}
            """

            # Get classification
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal case classifier skilled at creating concise, descriptive case titles that NEVER contain personally identifiable information."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            analysis = response.choices[0].message.content

            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "original_text": case_text,
                "cleaned_text": cleaned_text,
                "analysis": analysis
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def generate_final_summary(self, initial_analysis: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a final case summary using both AI-generated analysis and user-provided form data.

        Args:
            initial_analysis (Dict[str, Any]): AI-generated case analysis.
            form_data (Dict[str, Any]): Completed legal form data.

        Returns:
            Dict containing the final case summary.
        """
        try:
            # Parse the analysis JSON if it's a string
            if isinstance(initial_analysis.get("analysis"), str):
                analysis_data = json.loads(initial_analysis.get("analysis", "{}"))
            else:
                analysis_data = initial_analysis.get("analysis", {})
            
            category = analysis_data.get("category", "Unknown")
            subcategory = analysis_data.get("subcategory", "Unknown")
            key_details = analysis_data.get("key_details", "No details extracted.")
            
            # Use the AI-generated title if available, otherwise generate a specific one
            case_title = analysis_data.get("case_title")
            if not case_title:
                # Request a specific title based on form data
                title_prompt = f"""Generate a specific, descriptive title (MAXIMUM 70 characters) for this {category} - {subcategory} case based on these details:
                
                Key details: {key_details}
                Form data: {form_data}
                
                The title MUST NOT contain any personally identifiable information (PII) such as names, addresses, specific dates, or unique identifiers.
                
                Focus on the legal situation, not the individuals involved.
                Examples of good titles:
                - "Interstate Adoption with Biological Parent Consent"
                - "Workplace Discrimination Based on Religious Practices"
                - "Contested Foreclosure with Improper Notice Claims"
                
                YOUR RESPONSE MUST BE ONLY THE TITLE TEXT, MAXIMUM 70 CHARACTERS.
                """
                
                title_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You generate concise, specific legal case titles without any PII, maximum 70 characters."},
                        {"role": "user", "content": title_prompt}
                    ]
                )
                
                case_title = title_response.choices[0].message.content.strip('"').strip()
                
                # Ensure title is within 70 characters
                if len(case_title) > 70:
                    case_title = case_title[:67] + "..."
            else:
                # Ensure existing title is within 70 characters
                if len(case_title) > 70:
                    case_title = case_title[:67] + "..."
            
            # Create a prompt that combines AI-generated insights and form responses
            prompt = f"""You are a professional legal summarizer assisting a {category} attorney specializing in {subcategory} cases in reviewing potential client leads.

Follow these guidelines:
1. STRICTLY FORBIDDEN: Do not include or reference the original case description.
2. STRICTLY FORBIDDEN: Remove ALL Personally Identifiable Information (PII).
3. Each bullet point should be a complete, professional statement.
4. Use formal legal terminology relevant to {category} cases.
5. Focus only on legal aspects, requirements, and considerations.
6. Use <ul> and <li> tags for bullet points.
7. Ensure descriptions are abstract and applicable to similar cases.

### **Initial AI-Extracted Key Details:**
{key_details}

### **User-Provided Form Responses:**
{form_data}

Now, create a structured case summary:
{{
  "title": "{case_title}",
  "summary": "HTML formatted summary with sections:
              <h3>General Case Summary</h3>
              <ul>
                [3-4 bullet points summarizing core legal situation]
              </ul>
              <h3>Key aspects of the case</h3>
              <ul>
                [4-5 bullet points listing key legal components]
              </ul>
              <h3>Potential Merits of the Case</h3>
              <ul>
                [4-5 bullet points analyzing legal strategies and potential outcomes]
              </ul>"
}}"""

            # Get GPT-4o summary
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a legal document summarizer."},
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.choices[0].message.content

            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }