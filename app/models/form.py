import re
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto

class FormStatus(Enum):
    """Enum for form status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class FormType(Enum):
    """Enum for form types"""
    INTAKE = "intake"
    SUPPLEMENTARY = "supplementary"
    REVIEW = "review"
    APPEAL = "appeal"

class FieldType(Enum):
    """Enum for form field types"""
    TEXT = "text"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    DATE = "date"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    CURRENCY = "currency"
    PHONE = "phone"
    EMAIL = "email"

@dataclass
class FormField:
    """Represents a single form field"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    options: List[Dict[str, str]] = field(default_factory=list)
    default_value: Any = None
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "type": self.field_type.value,
            "required": self.required,
            "placeholder": self.placeholder,
            "helpText": self.help_text,
            "validationRules": self.validation_rules,
            "options": self.options,
            "defaultValue": self.default_value,
            "order": self.order
        }

@dataclass
class FormSection:
    """Represents a section of the form"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    fields: List[FormField] = field(default_factory=list)
    order: int = 0
    conditional_display: Dict[str, Any] = field(default_factory=dict)

    def add_field(self, field: FormField) -> None:
        """Add a field to the section"""
        field.order = len(self.fields)
        self.fields.append(field)

    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "fields": [field.to_dict() for field in sorted(self.fields, key=lambda x: x.order)],
            "order": self.order,
            "conditionalDisplay": self.conditional_display
        }

@dataclass
class FormMetadata:
    """Form metadata information"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    version: int = 1
    category: Optional[str] = None
    subcategory: Optional[str] = None

@dataclass
class Form:
    """Main form model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    form_type: FormType = FormType.INTAKE
    status: FormStatus = FormStatus.DRAFT
    sections: List[FormSection] = field(default_factory=list)
    metadata: FormMetadata = field(default_factory=FormMetadata)
    validation_schema: Dict[str, Any] = field(default_factory=dict)
    submission_data: Dict[str, Any] = field(default_factory=dict)
    files: List[Dict[str, Any]] = field(default_factory=list)

    def add_section(self, section: FormSection) -> None:
        """Add a section to the form"""
        section.order = len(self.sections)
        self.sections.append(section)

    def validate_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate form submission data
        
        Args:
            data: Dictionary of form data
            
        Returns:
            Dictionary with validation results
        """
        errors = {}
        for section in self.sections:
            for field in section.fields:
                field_name = field.name
                field_value = data.get(field_name)

                # Check required fields
                if field.required and not field_value:
                    errors[field_name] = f"{field.label} is required"
                    continue

                # Apply validation rules if value exists
                if field_value and field.validation_rules:
                    for rule, rule_value in field.validation_rules.items():
                        # Implement validation logic for each rule type
                        validation_result = self._validate_field(
                            field_value, rule, rule_value
                        )
                        if not validation_result['valid']:
                            errors[field_name] = validation_result['message']

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def _validate_field(self, value: Any, rule: str, rule_value: Any) -> Dict[str, Any]:
        """
        Validate a single field value against a rule
        
        Args:
            value: Field value to validate
            rule: Validation rule name
            rule_value: Value to validate against
            
        Returns:
            Dictionary with validation result
        """
        # Implement specific validation rules
        validation_rules = {
            "min_length": lambda v, r: len(str(v)) >= r,
            "max_length": lambda v, r: len(str(v)) <= r,
            "pattern": lambda v, r: bool(re.match(r, str(v))),
            "min_value": lambda v, r: float(v) >= r,
            "max_value": lambda v, r: float(v) <= r,
            "allowed_values": lambda v, r: v in r,
            # Add more validation rules as needed
        }

        if rule not in validation_rules:
            return {"valid": True, "message": ""}

        try:
            is_valid = validation_rules[rule](value, rule_value)
            return {
                "valid": is_valid,
                "message": f"Validation failed for rule: {rule}" if not is_valid else ""
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert form to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.form_type.value,
            "status": self.status.value,
            "sections": [section.to_dict() for section in sorted(self.sections, key=lambda x: x.order)],
            "metadata": {
                "createdAt": self.metadata.created_at.isoformat(),
                "updatedAt": self.metadata.updated_at.isoformat(),
                "createdBy": self.metadata.created_by,
                "lastModifiedBy": self.metadata.last_modified_by,
                "version": self.metadata.version,
                "category": self.metadata.category,
                "subcategory": self.metadata.subcategory
            },
            "validationSchema": self.validation_schema,
            "submissionData": self.submission_data,
            "files": self.files
        }

    @classmethod
    def create_from_template(cls, template: Dict[str, Any]) -> 'Form':
        """
        Create a form instance from a template configuration
        
        Args:
            template: Form template configuration
            
        Returns:
            Form instance
        """
        form = cls(
            title=template['title'],
            description=template.get('description'),
            form_type=FormType[template.get('type', 'INTAKE').upper()]
        )

        # Add sections and fields from template
        for section_template in template.get('sections', []):
            section = FormSection(
                title=section_template['title'],
                description=section_template.get('description')
            )

            for field_template in section_template.get('fields', []):
                field = FormField(
                    name=field_template['name'],
                    label=field_template['label'],
                    field_type=FieldType[field_template['type'].upper()],
                    required=field_template.get('required', False),
                    placeholder=field_template.get('placeholder'),
                    help_text=field_template.get('helpText'),
                    validation_rules=field_template.get('validationRules', {}),
                    options=field_template.get('options', []),
                    default_value=field_template.get('defaultValue')
                )
                section.add_field(field)

            form.add_section(section)

        return form

    def update_submission_data(self, data: Dict[str, Any]) -> None:
        """
        Update form submission data
        
        Args:
            data: New form data
        """
        self.submission_data.update(data)
        self.metadata.updated_at = datetime.utcnow()
        self.metadata.version += 1