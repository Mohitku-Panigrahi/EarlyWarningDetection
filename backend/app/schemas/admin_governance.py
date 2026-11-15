from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Governance Overview ---

class AttentionQueueItem(BaseModel):
    case_id: str
    student_id: int
    student_name: str
    registration_number: str
    section: str
    mentor_id: int
    mentor_name: str
    issue_type: str  # "Overdue Task", "Declining Trajectory", "Awaiting Follow-up", "Pending Decision", "Overdue Follow-up"
    severity: str    # "high", "medium", "low"
    detail: str
    action_label: str

class GovernanceOverviewResponse(BaseModel):
    total_active_mentors: int
    total_assigned_students: int
    students_with_active_support: int
    students_awaiting_followup: int
    pending_intervention_decisions: int
    overdue_followups_count: int
    attention_queue: List[AttentionQueueItem]

class MentorWorkloadItem(BaseModel):
    mentor_id: int
    faculty_code: str
    mentor_name: str
    department: str
    assigned_students: int
    max_quota: int
    remaining_capacity: int
    allocated_percentage: float

class StudentDistributionItem(BaseModel):
    mentor_id: int
    faculty_code: str
    mentor_name: str
    total_students: int
    on_track_count: int
    on_track_pct: float
    watch_count: int
    watch_pct: float
    needs_review_count: int
    needs_review_pct: float

# --- Mentor Performance & Directory ---

class MentorDirectoryItem(BaseModel):
    mentor_id: int
    faculty_code: str
    name: str
    department: str
    designation: str
    assigned_students: int
    capacity_utilization_pct: float
    on_track_count: int
    watch_count: int
    needs_review_count: int
    pending_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_meetings: int
    pending_intervention_approvals: int

class MentorGovernanceProfileResponse(BaseModel):
    mentor_id: int
    faculty_code: str
    name: str
    department: str
    designation: str
    workload_cap: int
    
    # Group 1: Assigned cohort
    total_assigned_students: int
    cohort_status_distribution: Dict[str, int]
    avg_attendance_pct: float
    avg_assessment_pct: float
    students_requiring_attention: int
    
    # Group 2: Academic support activity
    tasks_assigned: int
    tasks_completed: int
    tasks_in_progress: int
    tasks_overdue: int
    students_with_uncompleted_tasks: int
    
    # Group 3: Mentoring engagement
    total_meetings: int
    unique_students_met: int
    students_without_meeting: int
    followups_scheduled: int
    followups_overdue: int
    meeting_frequency_weekly: Dict[str, int]
    
    # Group 4: Intervention management
    recommendations_awaiting_approval: int
    approved_interventions: int
    dismissed_recommendations: int
    completed_interventions: int

# --- Student-Mentor Relationships ---

class StudentMentorRelationshipItem(BaseModel):
    student_id: int
    student_name: str
    registration_number: str
    section: str
    mentor_id: Optional[int] = None
    mentor_name: Optional[str] = None
    faculty_code: Optional[str] = None
    academic_status: str
    attendance_pct: float
    assessment_pct: float
    active_tasks_count: int
    completed_tasks_count: int
    last_meeting_date: Optional[datetime] = None
    next_followup_date: Optional[datetime] = None
    support_status: str  # "Active Mentoring", "Awaiting Follow-up", "Pending Tasks", "Standard Tracking"

class StudentMentorRelationshipResponse(BaseModel):
    total: int
    page: int
    page_size: int
    relationships: List[StudentMentorRelationshipItem]

class StudentGovernanceDetailResponse(BaseModel):
    student_id: int
    name: str
    registration_number: str
    section: str
    department: str
    academic_status: str
    cgpa: float
    attendance_pct: float
    internal_marks_pct: float
    
    # Mentor info
    mentor_id: Optional[int] = None
    mentor_name: Optional[str] = None
    faculty_code: Optional[str] = None
    
    # Academic Progress
    observed_trajectory: List[Dict[str, Any]]
    projected_trajectory: List[Dict[str, Any]]
    weak_subjects: List[Dict[str, Any]]
    
    # Mentoring Activity
    meetings: List[Dict[str, Any]]
    upcoming_followup: Optional[datetime] = None
    
    # Task Progress
    tasks: List[Dict[str, Any]]
    
    # Intervention History
    interventions: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]

# --- Meeting Monitoring ---

class MeetingAnalyticsResponse(BaseModel):
    total_meetings: int
    unique_students_met: int
    students_without_recorded_meeting: int
    meetings_by_mentor: Dict[str, int]
    meetings_by_modality: Dict[str, int]
    weekly_frequency: Dict[str, int]
    upcoming_followups_count: int
    overdue_followups_count: int

class FollowupQueueItem(BaseModel):
    meeting_id: int
    student_id: int
    student_name: str
    registration_number: str
    section: str
    mentor_id: int
    mentor_name: str
    meeting_date: datetime
    next_followup_date: datetime
    days_difference: int  # negative if overdue, positive if upcoming
    status: str           # "Upcoming", "Overdue"
    agreed_actions: Optional[str] = None

# --- Intervention Oversight ---

class AdminInterventionItem(BaseModel):
    id: int
    student_id: int
    student_name: str
    registration_number: str
    section: str
    mentor_id: int
    mentor_name: str
    intervention_type: str
    course_code: Optional[str] = None
    priority: str
    status: str
    recommendation: str
    reason: str
    created_at: datetime
    updated_at: datetime
    associated_tasks: List[Dict[str, Any]]
    decisions_count: int
    admin_reviewed: bool = False
    admin_notes: Optional[str] = None

class AdminInterventionReviewRequest(BaseModel):
    action: str = Field(..., description="flag_for_review, request_clarification, add_administrative_note")
    note: str = Field(..., min_length=3, max_length=1000)
