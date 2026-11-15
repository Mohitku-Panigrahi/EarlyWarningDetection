from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class StudentKpiData(BaseModel):
    academic_status: str  # ON TRACK, WATCH, NEEDS REVIEW
    status_subtitle: str
    status_color: str  # amber, green, red
    semester_average: float
    cgpa: float
    prev_sem_diff: float
    attendance_percentage: float
    attendance_target: float = 85.0
    classes_to_safe: int
    assignment_completion_pct: float
    assignments_completed: int
    assignments_total: int
    assignments_pending: int

class WeeklyTrendPoint(BaseModel):
    week_number: int
    week_label: str
    attendance_pct: float
    assessment_score: float
    is_current: bool = False
    is_projected: bool = False

class SubjectPerformanceItem(BaseModel):
    subject_code: str
    subject_name: str
    internal_marks: float
    maximum_internal_marks: float = 30.0
    internal_marks_pct: float
    attendance_pct: float
    assignment_completion_pct: float
    is_below_cutoff: bool = False

class TaskItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    course: Optional[str] = None
    priority: str  # High, Medium, Low
    status: str    # pending, in_progress, completed, overdue
    due_label: str
    source: str    # mentor, student, playbook
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    creator_name: Optional[str] = None

class TaskToggleRequest(BaseModel):
    status: Optional[str] = Field(None, description="Target status: 'pending', 'in_progress', 'completed'")

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=256)
    description: Optional[str] = None
    course_code: Optional[str] = None
    priority: str = "Medium"
    due_date: Optional[datetime] = None

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class ExplanationFactor(BaseModel):
    factor_title: str
    factor_description: str
    severity: str  # warning, info, success
    icon: str

class RecommendedAction(BaseModel):
    step_number: int
    title: str
    description: str

class StudentExplanationResponse(BaseModel):
    academic_status: str
    summary: str
    factors: List[ExplanationFactor]
    next_steps: List[RecommendedAction]
    clearance_weeks_remaining: int = 4

class StudentDashboardResponse(BaseModel):
    student_id: int
    registration_number: str
    name: str
    section: str
    department: str
    programme: str
    semester: int
    term_metadata: str
    kpi: StudentKpiData
    weekly_trends: List[WeeklyTrendPoint]
    subject_performances: List[SubjectPerformanceItem]
    tasks: List[TaskItem]
    explanation: StudentExplanationResponse
