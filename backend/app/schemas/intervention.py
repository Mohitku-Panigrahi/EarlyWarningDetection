from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class InterventionCreate(BaseModel):
    student_id: int
    intervention_type: str = Field(..., description="e.g. Subject Tutoring & Practice, Attendance Recovery, Academic Counseling")
    recommendation: str = Field(..., min_length=5)
    reason: str = Field(..., min_length=5)
    priority: str = Field("Medium", description="High, Medium, Low")
    playbook_id: Optional[str] = None

class InterventionUpdate(BaseModel):
    intervention_type: Optional[str] = None
    recommendation: Optional[str] = None
    reason: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class InterventionActionRequest(BaseModel):
    comments: Optional[str] = Field("", description="Mentor rationale or feedback for decision")

class MentorDecisionItem(BaseModel):
    id: int
    decision: str
    comments: Optional[str]
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterventionResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    registration_number: str
    mentor_id: int
    mentor_name: str
    intervention_type: str
    recommendation: str
    reason: str
    priority: str
    status: str  # proposed, approved, rejected, in_progress, completed
    created_at: datetime
    updated_at: datetime
    decisions: List[MentorDecisionItem] = []

    model_config = ConfigDict(from_attributes=True)
