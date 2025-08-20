from datetime import datetime
import uuid
from typing import Dict, Optional, List, Any
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Union

class CaseStatus(Enum):
    """Enum for case status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ConfidenceLevel(Enum):
    """Enum for AI confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CaseMetadata:
    """Metadata for a legal case"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    assigned_to: Optional[str] = None

@dataclass
class CategoryPrediction:
    """Category prediction result"""
    main_category: str
    sub_category: str
    confidence: ConfidenceLevel
    confidence_score: float
    prediction_timestamp: datetime = field(default_factory=datetime.utcnow)
    alternative_categories: List[str] = field(default_factory=list)

@dataclass
class Case:
    """Main case model"""
    # Basic identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reference_number: str = field(default_factory=lambda: f"CASE-{str(uuid.uuid4())[:8].upper()}")
    
    # Case details
    title: str
    description: str
    status: CaseStatus = field(default=CaseStatus.DRAFT)
    
    # Category information
    main_category: str
    sub_category: str
    category_prediction: Optional[CategoryPrediction] = None
    
    # Form data
    form_data: Dict[str, Any] = field(default_factory=dict)
    files: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps and metadata
    metadata: CaseMetadata = field(default_factory=CaseMetadata)
    
    # Additional fields
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    notes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """
        Convert case to dictionary with optional sensitive data filtering
        
        Args:
            include_sensitive (bool): Whether to include all details
        """
        base_dict = {
            "id": self.id,
            "reference_number": self.reference_number,
            "title": self.title,
            "status": self.status.value,
            "main_category": self.main_category,
            "sub_category": self.sub_category,
            "tags": self.tags,
            "priority": self.priority
        }

        if include_sensitive:
            base_dict.update({
                "description": self.description,
                "form_data": self.form_data,
                "files": self.files,
                "notes": self.notes
            })

        # Handle category prediction
        if self.category_prediction:
            base_dict["category_prediction"] = {
                "main_category": self.category_prediction.main_category,
                "sub_category": self.category_prediction.sub_category,
                "confidence": self.category_prediction.confidence.value,
                "confidence_score": self.category_prediction.confidence_score,
                "prediction_timestamp": self.category_prediction.prediction_timestamp.isoformat(),
                "alternative_categories": self.category_prediction.alternative_categories
            }

        # Handle metadata
        base_dict["metadata"] = {
            key: getattr(self.metadata, key).isoformat() if isinstance(getattr(self.metadata, key), datetime) else getattr(self.metadata, key)
            for key in ['created_at', 'updated_at', 'submitted_at', 'reviewed_at', 'completed_at', 'created_by', 'reviewed_by', 'assigned_to']
        }

        return base_dict

    def get_activity_log(self) -> List[Dict[str, Any]]:
        """
        Generate a comprehensive activity log
        
        Returns:
            List of activity log entries
        """
        log = []
        
        # Status changes
        log.append({
            "type": "status_change",
            "status": self.status.value,
            "timestamp": self.metadata.updated_at.isoformat()
        })
        
        # Notes
        log.extend([
            {
                "type": "note_added",
                "content": note.get('content', ''),
                "author": note.get('author', ''),
                "timestamp": note.get('created_at', '')
            } for note in self.notes
        ])
        
        # File uploads
        log.extend([
            {
                "type": "file_uploaded",
                "filename": file.get('filename', ''),
                "timestamp": file.get('uploaded_at', '')
            } for file in self.files
        ])
        
        return sorted(log, key=lambda x: x.get('timestamp', ''))

    def get_timeline(self) -> Dict[str, datetime]:
        """
        Get key timeline events
        
        Returns:
            Dictionary of timeline events
        """
        return {
            "created": self.metadata.created_at,
            "submitted": self.metadata.submitted_at,
            "reviewed": self.metadata.reviewed_at,
            "completed": self.metadata.completed_at
        }

    def set_questionnaire_analysis(self, category: str, subcategory: str, 
                                 confidence_score: int = 85, summary: str = "") -> None:
        """
        Set analysis results for questionnaire-based submissions.
        Fast path that bypasses complex AI analysis.
        
        Args:
            category (str): Legal category from questionnaire
            subcategory (str): Legal subcategory from questionnaire
            confidence_score (int): Confidence score (default 85 for questionnaire)
            summary (str): Optional summary text
        """
        self.main_category = category
        self.sub_category = subcategory
        
        # Create simple category prediction for questionnaire method
        self.category_prediction = CategoryPrediction(
            main_category=category,
            sub_category=subcategory,
            confidence=ConfidenceLevel.HIGH if confidence_score >= 80 else ConfidenceLevel.MEDIUM,
            confidence_score=float(confidence_score),
            prediction_timestamp=datetime.utcnow(),
            alternative_categories=[]
        )
        
        # Update metadata
        self.metadata.updated_at = datetime.utcnow()
        
        # Add note about method used
        self.notes.append({
            "content": f"Case classified using questionnaire method: {category} - {subcategory}",
            "author": "system",
            "created_at": datetime.utcnow().isoformat(),
            "type": "system_classification",
            "method": "questionnaire",
            "confidence_score": confidence_score
        })

    def to_questionnaire_summary(self) -> Dict[str, Any]:
        """
        Generate a summary optimized for questionnaire-based cases.
        Returns essential information without complex AI analysis details.
        
        Returns:
            Dict containing questionnaire case summary
        """
        return {
            "id": self.id,
            "reference_number": self.reference_number,
            "title": self.title,
            "status": self.status.value,
            "category": self.main_category,
            "subcategory": self.sub_category,
            "confidence": self.category_prediction.confidence.value if self.category_prediction else "medium",
            "confidence_score": self.category_prediction.confidence_score if self.category_prediction else 70,
            "method": "questionnaire",
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
            "submitted_at": self.metadata.submitted_at.isoformat() if self.metadata.submitted_at else None,
            "priority": self.priority,
            "tags": self.tags,
            "form_responses": len(self.form_data.get('responses', [])) if self.form_data else 0,
            "processing_method": "questionnaire",
            "is_questionnaire_based": True
        }

    def update_questionnaire_status(self, new_status: CaseStatus, updated_by: str = "system") -> None:
        """
        Update case status for questionnaire submissions with proper tracking.
        
        Args:
            new_status (CaseStatus): New status to set
            updated_by (str): Who updated the status
        """
        old_status = self.status.value
        self.status = new_status
        self.metadata.updated_at = datetime.utcnow()
        
        # Track status change
        self.notes.append({
            "content": f"Status changed from {old_status} to {new_status.value}",
            "author": updated_by,
            "created_at": datetime.utcnow().isoformat(),
            "type": "status_change",
            "old_status": old_status,
            "new_status": new_status.value
        })

        # Set specific timestamps based on status
        if new_status == CaseStatus.SUBMITTED:
            self.metadata.submitted_at = datetime.utcnow()
        elif new_status == CaseStatus.IN_REVIEW:
            self.metadata.reviewed_at = datetime.utcnow()
        elif new_status == CaseStatus.COMPLETED:
            self.metadata.completed_at = datetime.utcnow()

    def add_questionnaire_data(self, form_responses: Dict[str, Any], 
                             case_summary: str, user_info: Dict[str, str]) -> None:
        """
        Add questionnaire form data and user information to the case.
        
        Args:
            form_responses (Dict): User's form responses
            case_summary (str): User's case summary
            user_info (Dict): User contact information
        """
        # Store form data
        self.form_data.update({
            "questionnaire_responses": form_responses,
            "case_summary": case_summary,
            "user_info": user_info,
            "submission_method": "questionnaire",
            "submission_timestamp": datetime.utcnow().isoformat()
        })
        
        # Update description with case summary
        if case_summary and len(case_summary.strip()) > len(self.description.strip()):
            self.description = case_summary.strip()
        
        # Add relevant tags
        if "questionnaire" not in self.tags:
            self.tags.append("questionnaire")
        if "form-submission" not in self.tags:
            self.tags.append("form-submission")
        
        # Add note about data addition
        self.notes.append({
            "content": f"Questionnaire data added: {len(form_responses)} responses",
            "author": "system",
            "created_at": datetime.utcnow().isoformat(),
            "type": "data_update",
            "response_count": len(form_responses)
        })

    def get_questionnaire_metrics(self) -> Dict[str, Any]:
        """
        Get metrics specific to questionnaire-based cases.
        
        Returns:
            Dict containing questionnaire metrics
        """
        questionnaire_data = self.form_data.get("questionnaire_responses", {})
        
        return {
            "submission_method": "questionnaire",
            "form_responses_count": len(questionnaire_data),
            "case_summary_length": len(self.form_data.get("case_summary", "")),
            "confidence_score": self.category_prediction.confidence_score if self.category_prediction else 0,
            "confidence_level": self.category_prediction.confidence.value if self.category_prediction else "unknown",
            "processing_time_fast": True,  # Questionnaire method is fast
            "requires_manual_review": self.category_prediction.confidence_score < 70 if self.category_prediction else True,
            "category_pre_selected": True,  # Category was selected by user
            "created_at": self.metadata.created_at.isoformat(),
            "last_updated": self.metadata.updated_at.isoformat(),
            "tags": self.tags,
            "priority": self.priority
        }

# Additional utility functions
def create_case_from_summary(summary: str, user_id: str) -> Case:
    """
    Factory method to create a case from a summary
    
    Args:
        summary (str): Initial case summary
        user_id (str): ID of the user creating the case
    
    Returns:
        Case: Newly created case instance
    """
    return Case(
        title=summary[:100],  # Truncate to first 100 characters
        description=summary,
        main_category="Uncategorized",
        sub_category="Pending",
        metadata=CaseMetadata(created_by=user_id)
    )

def create_questionnaire_case(form_data: Dict[str, Any], category: str, 
                            subcategory: str, user_id: str) -> Case:
    """
    Factory method to create a case specifically for questionnaire submissions.
    Optimized for speed and simplicity.
    
    Args:
        form_data (Dict): Complete form data from questionnaire
        category (str): Pre-selected legal category
        subcategory (str): Pre-selected legal subcategory  
        user_id (str): ID of the user creating the case
    
    Returns:
        Case: Newly created questionnaire-based case instance
    """
    # Extract basic info from form data
    case_summary = form_data.get('caseSummary', '')
    full_name = form_data.get('fullName', 'Client')
    
    # Create a professional title
    title = f"{subcategory} - {full_name}" if full_name != 'Client' else f"{subcategory} Legal Matter"
    
    # Limit title length
    if len(title) > 100:
        title = title[:97] + "..."
    
    # Create case with questionnaire-specific setup
    case = Case(
        title=title,
        description=case_summary[:1000],  # Limit description length
        main_category=category,
        sub_category=subcategory,
        form_data={},  # Will be populated by add_questionnaire_data
        metadata=CaseMetadata(created_by=user_id),
        tags=["questionnaire", "form-submission"],
        priority=1  # Standard priority for questionnaire cases
    )
    
    # Set high confidence since category was pre-selected
    case.set_questionnaire_analysis(category, subcategory, confidence_score=85)
    
    # Add form data
    user_info = {
        "full_name": form_data.get('fullName', ''),
        "residing_zipcode": form_data.get('residingZipcode', ''),
        "city": form_data.get('city', ''),
        "state": form_data.get('state', ''),
        "county": form_data.get('county', '')
    }
    
    # Extract form responses (excluding basic info)
    form_responses = {k: v for k, v in form_data.items() 
                     if k not in ['caseSummary', 'fullName', 'residingZipcode', 'city', 'state', 'county']}
    
    case.add_questionnaire_data(form_responses, case_summary, user_info)
    
    return case

def create_ai_analysis_case(case_summary: str, ai_analysis: Dict[str, Any], user_id: str) -> Case:
    """
    Factory method to create a case from AI analysis results.
    For cases that went through the full AI pipeline.
    
    Args:
        case_summary (str): Original case description
        ai_analysis (Dict): Complete AI analysis results
        user_id (str): ID of the user creating the case
    
    Returns:
        Case: Newly created AI-analyzed case instance
    """
    category = ai_analysis.get('category', 'Unknown')
    subcategory = ai_analysis.get('subcategory', 'General')
    confidence_score = ai_analysis.get('confidence_score', 50)
    
    # Create title from AI analysis or case summary
    title = ai_analysis.get('case_title', case_summary[:100])
    if len(title) > 100:
        title = title[:97] + "..."
    
    case = Case(
        title=title,
        description=case_summary,
        main_category=category,
        sub_category=subcategory,
        metadata=CaseMetadata(created_by=user_id),
        tags=["ai-analyzed", "full-analysis"],
        priority=2 if confidence_score < 60 else 1  # Higher priority for low confidence
    )
    
    # Set category prediction from AI analysis
    case.category_prediction = CategoryPrediction(
        main_category=category,
        sub_category=subcategory,
        confidence=ConfidenceLevel.HIGH if confidence_score >= 75 else 
                  ConfidenceLevel.MEDIUM if confidence_score >= 40 else ConfidenceLevel.LOW,
        confidence_score=float(confidence_score),
        prediction_timestamp=datetime.utcnow(),
        alternative_categories=ai_analysis.get('secondary_issues', [])
    )
    
    # Store AI analysis results
    case.form_data = {
        "ai_analysis": ai_analysis,
        "processing_method": ai_analysis.get('method', 'ai_analysis'),
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "processing_time": ai_analysis.get('total_processing_time', 0),
        "agents_consulted": ai_analysis.get('agents_consulted', []),
        "confidence_consensus": ai_analysis.get('confidence_consensus', confidence_score)
    }
    
    # Add analysis note
    case.notes.append({
        "content": f"Case analyzed using AI method: {category} - {subcategory} (Confidence: {confidence_score}/100)",
        "author": "system",
        "created_at": datetime.utcnow().isoformat(),
        "type": "ai_analysis",
        "method": "ai_pipeline",
        "confidence_score": confidence_score,
        "processing_time": ai_analysis.get('total_processing_time', 0)
    })
    
    return case

# Validation functions
def validate_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate case data before creation.
    
    Args:
        case_data (Dict): Case data to validate
    
    Returns:
        Dict: Validation result with is_valid and issues
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "warnings": []
    }
    
    # Required fields
    required_fields = ["title", "description", "main_category", "sub_category"]
    for field in required_fields:
        if not case_data.get(field):
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Missing required field: {field}")
    
    # Title length
    title = case_data.get("title", "")
    if len(title) > 200:
        validation_result["warnings"].append("Title is longer than 200 characters")
    
    # Description length
    description = case_data.get("description", "")
    if len(description) > 10000:
        validation_result["warnings"].append("Description is longer than 10,000 characters")
    elif len(description) < 10:
        validation_result["issues"].append("Description is too short (minimum 10 characters)")
        validation_result["is_valid"] = False
    
    return validation_result