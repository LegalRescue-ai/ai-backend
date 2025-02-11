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