# form_generator.py

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field

# Field type definitions
class FieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    DATE = "date"
    NUMBER = "number"
    EMAIL = "email"
    TEL = "tel"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"

class FormType(Enum):
    INTAKE = "intake"
    SUPPLEMENTARY = "supplementary"
    REVIEW = "review"
    APPEAL = "appeal"

class FormStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class FormField:
    """Represents a form field"""
    name: str
    label: str
    type: FieldType
    required: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)
    default_value: Any = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type.value,
            "required": self.required,
            "validationRules": self.validation_rules,
            "options": self.options,
            "defaultValue": self.default_value,
            "placeholder": self.placeholder,
            "helpText": self.help_text,
            "order": self.order
        }

@dataclass
class FormSection:
    """Represents a form section"""
    title: str
    fields: List[FormField] = field(default_factory=list)
    description: Optional[str] = None
    order: int = 0

    def add_field(self, field: FormField) -> None:
        field.order = len(self.fields)
        self.fields.append(field)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "fields": [field.to_dict() for field in sorted(self.fields, key=lambda x: x.order)],
            "order": self.order
        }

@dataclass
class Form:
    """Represents a complete form"""
    title: str
    category: str
    subcategory: str
    sections: List[FormSection] = field(default_factory=list)
    description: Optional[str] = None
    form_type: FormType = FormType.INTAKE
    status: FormStatus = FormStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_section(self, section: FormSection) -> None:
        section.order = len(self.sections)
        self.sections.append(section)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "subcategory": self.subcategory,
            "description": self.description,
            "type": self.form_type.value,
            "status": self.status.value,
            "sections": [section.to_dict() for section in sorted(self.sections, key=lambda x: x.order)],
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }

class CategoryManager:
    """Simple category manager for validation"""
    def __init__(self):
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

    def validate_category(self, category: str, subcategory: str) -> bool:
        if category not in self.categories:
            return False
        return subcategory in self.categories[category]

class FormGenerator:
    """Advanced form generation system"""
    
    def __init__(self):
        self.category_manager = CategoryManager()

    def generate_form(self, category: str, subcategory: str) -> Form:
        """Generate a dynamic form based on category and subcategory"""
        if not self.category_manager.validate_category(category, subcategory):
            raise ValueError(f"Invalid category or subcategory: {category} - {subcategory}")

        # Map categories to their specific generators
        generators = {
            "Family Law": self._generate_family_law_form,
            "Employment Law": self._generate_employment_law_form,
            "Criminal Law": self._generate_criminal_law_form,
            "Real Estate Law": self._generate_real_estate_law_form,
            "Business/Corporate Law": self._generate_business_corporate_law_form,
            "Immigration Law": self._generate_immigration_law_form,
            "Personal Injury Law": self._generate_personal_injury_law_form,
            "Wills, Trusts, & Estates Law": self._generate_wills_trusts_estates_law_form,
            "Bankruptcy, Finances, & Tax Law": self._generate_bankruptcy_finances_tax_law_form,
            "Government & Administrative Law": self._generate_government_administrative_law_form,
            "Product & Services Liability Law": self._generate_product_services_liability_law_form,
            "Intellectual Property Law": self._generate_intellectual_property_law_form,
            "Landlord/Tenant Law": self._generate_landlord_tenant_law_form
        }

        # Get appropriate generator or use default
        generator = generators.get(category, self._generate_default_form)
        return generator(category, subcategory)

    def _generate_default_form(self, category: str, subcategory: str) -> Form:
        """Generate a generic form"""
        form = Form(
            title=f"{subcategory} Intake Form",
            category=category,
            subcategory=subcategory,
            description=f"Intake form for {category} - {subcategory}"
        )

        # Add personal information section
        personal_section = FormSection(
            title="Personal Information",
            description="Please provide your contact details"
        )
        personal_section.add_field(
            FormField(
                name="full_name",
                label="Full Name",
                type=FieldType.TEXT,
                required=True,
                validation_rules={"min_length": 2, "max_length": 100}
            )
        )
        personal_section.add_field(
            FormField(
                name="email",
                label="Email Address",
                type=FieldType.EMAIL,
                required=True,
                validation_rules={"pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}
            )
        )
        personal_section.add_field(
            FormField(
                name="phone",
                label="Phone Number",
                type=FieldType.TEL,
                required=True,
                validation_rules={"pattern": r'^\+?1?\d{10,14}$'}
            )
        )

        # Add case information section
        case_section = FormSection(
            title="Case Information",
            description="Provide details about your legal matter"
        )
        case_section.add_field(
            FormField(
                name="description",
                label="Case Description",
                type=FieldType.TEXTAREA,
                required=True,
                validation_rules={"min_length": 50, "max_length": 5000},
                placeholder="Please describe your legal issue in detail"
            )
        )

        form.add_section(personal_section)
        form.add_section(case_section)

        return form

    def _generate_family_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Family Law specific form"""
        form = self._generate_default_form(category, subcategory)

        # Add family law specific section
        family_section = FormSection(
            title="Family Details",
            description="Additional information needed for family law cases"
        )

        if subcategory == "Divorce":
            family_section.add_field(
                FormField(
                    name="marriage_date",
                    label="Date of Marriage",
                    type=FieldType.DATE,
                    required=True
                )
            )
            family_section.add_field(
                FormField(
                    name="separation_date",
                    label="Date of Separation",
                    type=FieldType.DATE,
                    required=False
                )
            )

        form.add_section(family_section)
        return form

    def _generate_employment_law_form(self, category: str, subcategory: str) -> Form:
        """Generate an Employment Law specific form"""
        form = self._generate_default_form(category, subcategory)

        # Add employment law specific section
        employment_section = FormSection(
            title="Employment Details",
            description="Information about your employment"
        )
        employment_section.add_field(
            FormField(
                name="employer",
                label="Employer Name",
                type=FieldType.TEXT,
                required=True
            )
        )
        employment_section.add_field(
            FormField(
                name="employment_date",
                label="Employment Start Date",
                type=FieldType.DATE,
                required=True
            )
        )

        form.add_section(employment_section)
        return form

    def _generate_criminal_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Criminal Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        criminal_section = FormSection(
            title="Criminal Case Details",
            description="Information about the criminal matter"
        )
        criminal_section.add_field(
            FormField(
                name="incident_date",
                label="Date of Incident",
                type=FieldType.DATE,
                required=True
            )
        )
        criminal_section.add_field(
            FormField(
                name="arrest_status",
                label="Current Status",
                type=FieldType.SELECT,
                options=["Under Investigation", "Arrested", "Charged", "On Bail", "Not Applicable"],
                required=True
            )
        )
        criminal_section.add_field(
            FormField(
                name="court_date",
                label="Next Court Date (if applicable)",
                type=FieldType.DATE,
                required=False
            )
        )
        
        form.add_section(criminal_section)
        return form

    def _generate_real_estate_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Real Estate Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        property_section = FormSection(
            title="Property Information",
            description="Details about the property involved"
        )
        property_section.add_field(
            FormField(
                name="property_address",
                label="Property Address",
                type=FieldType.TEXT,
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="property_type",
                label="Property Type",
                type=FieldType.SELECT,
                options=["Residential", "Commercial", "Industrial", "Land"],
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="estimated_value",
                label="Estimated Property Value",
                type=FieldType.NUMBER,
                required=True
            )
        )
        
        form.add_section(property_section)
        return form

    def _generate_business_corporate_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Business/Corporate Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        business_section = FormSection(
            title="Business Information",
            description="Details about the business entity"
        )
        business_section.add_field(
            FormField(
                name="business_name",
                label="Business Name",
                type=FieldType.TEXT,
                required=True
            )
        )
        business_section.add_field(
            FormField(
                name="business_type",
                label="Business Type",
                type=FieldType.SELECT,
                options=["Corporation", "LLC", "Partnership", "Sole Proprietorship"],
                required=True
            )
        )
        business_section.add_field(
            FormField(
                name="annual_revenue",
                label="Annual Revenue",
                type=FieldType.NUMBER,
                required=True
            )
        )
        
        form.add_section(business_section)
        return form

    def _generate_immigration_law_form(self, category: str, subcategory: str) -> Form:
        """Generate an Immigration Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        immigration_section = FormSection(
            title="Immigration Details",
            description="Information about immigration status"
        )
        immigration_section.add_field(
            FormField(
                name="citizenship",
                label="Current Citizenship",
                type=FieldType.TEXT,
                required=True
            )
        )
        immigration_section.add_field(
            FormField(
                name="visa_status",
                label="Current Visa Status",
                type=FieldType.SELECT,
                options=["None", "Tourist", "Student", "Work", "Permanent Resident"],
                required=True
            )
        )
        immigration_section.add_field(
            FormField(
                name="entry_date",
                label="Date of Entry to US",
                type=FieldType.DATE,
                required=True
            )
        )
        
        form.add_section(immigration_section)
        return form

    def _generate_personal_injury_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Personal Injury Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        injury_section = FormSection(
            title="Injury Information",
            description="Details about the injury"
        )
        injury_section.add_field(
            FormField(
                name="injury_date",
                label="Date of Injury",
                type=FieldType.DATE,
                required=True
            )
        )
        injury_section.add_field(
            FormField(
                name="injury_type",
                label="Type of Injury",
                type=FieldType.TEXT,
                required=True
            )
        )
        injury_section.add_field(
            FormField(
                name="medical_treatment",
                label="Medical Treatment Received",
                type=FieldType.TEXTAREA,
                required=True
            )
        )
        
        form.add_section(injury_section)
        return form

    def _generate_wills_trusts_estates_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Wills, Trusts, & Estates Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        estate_section = FormSection(
            title="Estate Information",
            description="Details about the estate or trust"
        )
        estate_section.add_field(
            FormField(
                name="estate_type",
                label="Type of Estate Matter",
                type=FieldType.SELECT,
                options=["Will Creation", "Trust Formation", "Probate", "Estate Administration"],
                required=True
            )
        )
        estate_section.add_field(
            FormField(
                name="estate_value",
                label="Estimated Estate Value",
                type=FieldType.NUMBER,
                required=True
            )
        )
        estate_section.add_field(
            FormField(
                name="beneficiaries",
                label="Number of Beneficiaries",
                type=FieldType.NUMBER,
                required=True
            )
        )
        
        form.add_section(estate_section)
        return form

    def _generate_bankruptcy_finances_tax_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Bankruptcy, Finances, & Tax Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        financial_section = FormSection(
            title="Financial Information",
            description="Details about financial situation"
        )
        financial_section.add_field(
            FormField(
                name="bankruptcy_type",
                label="Type of Bankruptcy",
                type=FieldType.SELECT,
                options=["Chapter 7", "Chapter 11", "Chapter 13"],
                required=True
            )
        )
        financial_section.add_field(
            FormField(
                name="total_debt",
                label="Total Debt Amount",
                type=FieldType.NUMBER,
                required=True
            )
        )
        financial_section.add_field(
            FormField(
                name="asset_value",
                label="Total Asset Value",
                type=FieldType.NUMBER,
                required=True
            )
        )
        
        form.add_section(financial_section)
        return form

    def _generate_government_administrative_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Government & Administrative Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        admin_section = FormSection(
            title="Administrative Details",
            description="Information about the administrative matter"
        )
        admin_section.add_field(
            FormField(
                name="agency",
                label="Government Agency Involved",
                type=FieldType.TEXT,
                required=True
            )
        )
        admin_section.add_field(
            FormField(
                name="case_number",
                label="Agency Case Number",
                type=FieldType.TEXT,
                required=False
            )
        )
        admin_section.add_field(
            FormField(
                name="hearing_date",
                label="Next Hearing Date",
                type=FieldType.DATE,
                required=False
            )
        )
        
        form.add_section(admin_section)
        return form

    def _generate_product_services_liability_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Product & Services Liability Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        liability_section = FormSection(
            title="Product/Service Information",
            description="Details about the product or service"
        )
        liability_section.add_field(
            FormField(
                name="product_name",
                label="Product/Service Name",
                type=FieldType.TEXT,
                required=True
            )
        )
        liability_section.add_field(
            FormField(
                name="purchase_date",
                label="Date of Purchase",
                type=FieldType.DATE,
                required=True
            )
        )
        liability_section.add_field(
            FormField(
                name="incident_date",
                label="Date of Incident",
                type=FieldType.DATE,
                required=True
            )
        )
        liability_section.add_field(
            FormField(
                name="damages",
                label="Description of Damages/Injuries",
                type=FieldType.TEXTAREA,
                required=True
            )
        )
        
        form.add_section(liability_section)
        return form

    def _generate_intellectual_property_law_form(self, category: str, subcategory: str) -> Form:
        """Generate an Intellectual Property Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        ip_section = FormSection(
            title="Intellectual Property Information",
            description="Details about the intellectual property"
        )
        ip_section.add_field(
            FormField(
                name="ip_type",
                label="Type of Intellectual Property",
                type=FieldType.SELECT,
                options=["Patent", "Trademark", "Copyright", "Trade Secret"],
                required=True
            )
        )
        ip_section.add_field(
            FormField(
                name="registration_status",
                label="Registration Status",
                type=FieldType.SELECT,
                options=["Not Registered", "Pending", "Registered", "Expired"],
                required=True
            )
        )
        ip_section.add_field(
            FormField(
                name="registration_number",
                label="Registration Number (if applicable)",
                type=FieldType.TEXT,
                required=False
            )
        )
        ip_section.add_field(
            FormField(
                name="creation_date",
                label="Date of Creation/First Use",
                type=FieldType.DATE,
                required=True
            )
        )
        
        form.add_section(ip_section)
        return form

    def _generate_landlord_tenant_law_form(self, category: str, subcategory: str) -> Form:
        """Generate a Landlord/Tenant Law specific form"""
        form = self._generate_default_form(category, subcategory)
        
        property_section = FormSection(
            title="Rental Property Information",
            description="Details about the rental property"
        )
        property_section.add_field(
            FormField(
                name="property_address",
                label="Property Address",
                type=FieldType.TEXT,
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="lease_type",
                label="Type of Lease",
                type=FieldType.SELECT,
                options=["Month-to-Month", "Fixed Term", "Sublease", "Commercial"],
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="lease_start",
                label="Lease Start Date",
                type=FieldType.DATE,
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="monthly_rent",
                label="Monthly Rent Amount",
                type=FieldType.NUMBER,
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="security_deposit",
                label="Security Deposit Amount",
                type=FieldType.NUMBER,
                required=True
            )
        )
        property_section.add_field(
            FormField(
                name="party_type",
                label="Are you the Landlord or Tenant?",
                type=FieldType.SELECT,
                options=["Landlord", "Tenant", "Property Manager"],
                required=True
            )
        )

        issue_section = FormSection(
            title="Issue Information",
            description="Details about the current issue"
        )
        issue_section.add_field(
            FormField(
                name="issue_type",
                label="Type of Issue",
                type=FieldType.SELECT,
                options=[
                    "Non-payment of Rent",
                    "Lease Violation",
                    "Property Damage",
                    "Maintenance Issue",
                    "Eviction",
                    "Security Deposit Dispute",
                    "Other"
                ],
                required=True
            )
        )
        issue_section.add_field(
            FormField(
                name="issue_date",
                label="Date Issue Began",
                type=FieldType.DATE,
                required=True
            )
        )
        issue_section.add_field(
            FormField(
                name="issue_description",
                label="Detailed Description of Issue",
                type=FieldType.TEXTAREA,
                required=True,
                validation_rules={"min_length": 50, "max_length": 2000}
            )
        )
        issue_section.add_field(
            FormField(
                name="prior_notice",
                label="Has Written Notice Been Given?",
                type=FieldType.SELECT,
                options=["Yes", "No"],
                required=True
            )
        )
        issue_section.add_field(
            FormField(
                name="notice_date",
                label="Date Notice Given (if applicable)",
                type=FieldType.DATE,
                required=False
            )
        )

        form.add_section(property_section)
        form.add_section(issue_section)
        return form

# Utility function for external use
def generate_legal_form(category: str, subcategory: str) -> Dict[str, Any]:
    """
    Generate a legal form based on category and subcategory
    
    Args:
        category: Main legal category
        subcategory: Specific subcategory
    
    Returns:
        Dictionary representation of the generated form
    """
    generator = FormGenerator()
    try:
        form = generator.generate_form(category, subcategory)
        return {
            "status": "success",
            "form": form.to_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }