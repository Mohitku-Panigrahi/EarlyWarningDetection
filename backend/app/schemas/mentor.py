from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MentorKpiData(BaseModel):
    total_mentees: int
    on_track_count: int
    on_track_pct: float
    watch_count: int
    watch_pct: float
    review_count: int
    review_pct: float

class MenteeListItem(BaseModel):
    student_id: int
    name: str
    registration_number: str
    section: str
    cgpa: float
    attendance_pct: float
    internal_score_pct: float
    academic_status: str  # ON TRACK, WATCH, NEEDS REVIEW
    risk_probability: float
    primary_concern: Optional[str] = None
    last_contact: str = "2 days ago"

class PriorityQueueItem(BaseModel):
    student_id: int
    name: str
    registration_number: str
    initials: str
    urgency: str  # High Urgency, Moderate
    status_label: str  # Needs Immediate Review, Academic Watch
    concern_summary: str
    proposed_intervention_id: Optional[int] = None

class MentorDashboardResponse(BaseModel):
    mentor_id: int
    mentor_name: str
    faculty_code: str
    department: str
    designation: str
    session_label: str = "2024–2025 Regular • Semester 4 (Spring)"
    cohort_label: str
    kpi: MentorKpiData
    priority_queue: List[PriorityQueueItem]
    mentees: List[MenteeListItem]

class ShapFeatureContribution(BaseModel):
    feature: str
    feature_name: str
    observed_value: str
    current_value: Optional[str] = None
    contribution: float
    direction: str  # positive_risk, negative_risk
    impact_label: str  # Increases predicted risk / Reduces predicted risk
    explanation: str

class RuleTraceItem(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    details: str
    threshold: Optional[str] = None
    observed_value: Optional[str] = None

class CounterfactualSimulation(BaseModel):
    scenario: str
    projected_probability: float
    projected_status: str
    target_actions: List[str]

class BayesianReasoning(BaseModel):
    prior: float
    evidence: str
    likelihood_ratio: float
    posterior: float

class MenteeRiskDetailResponse(BaseModel):
    student_id: int
    name: str
    registration_number: str
    section: str
    cgpa: float
    academic_status: str
    risk_probability: float
    decision_threshold: float = 0.40
    model_version: str = "v2.4-lpu (SHAP+Bayes)"
    explanation_summary: str
    shap_waterfall: List[ShapFeatureContribution]
    rules_fired: List[RuleTraceItem]
    counterfactual: CounterfactualSimulation
    bayesian: BayesianReasoning
    active_interventions: List[Dict[str, Any]]

class MentorWorkloadResponse(BaseModel):
    mentor_id: int
    faculty_code: str
    name: str
    department: str
    current_mentees: int
    workload_cap: int = 10
    utilization_pct: float
    pending_interventions_count: int

class MentorTaskAssignRequest(BaseModel):
    student_id: int
    course_code: Optional[str] = None
    title: str = Field(..., min_length=3, max_length=256)
    description: Optional[str] = None
    priority: str = Field("Medium", description="High, Medium, Low")
    due_date: Optional[datetime] = None

class MentorTaskItem(BaseModel):
    id: int
    student_id: int
    student_name: str
    registration_number: str
    section: str
    course_code: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    done_at: Optional[datetime] = None
    source: str

# ----------------- Phase 2 & 3 Analytics & Recommendation Schemas -----------------

class SubjectAverageItem(BaseModel):
    subject_code: str
    subject_name: str
    cohort_avg: float
    benchmark: float = 75.0
    students_below_count: int

class MentorCohortAnalytics(BaseModel):
    status_distribution: Dict[str, int]
    avg_cohort_attendance: float
    avg_cohort_assessment: float
    trajectory_distribution: Dict[str, int]  # improving, stable, declining
    pending_tasks_count: int
    subject_averages: List[SubjectAverageItem]

class WeeklyTrajectoryPoint(BaseModel):
    week_number: int
    assessment_score: float
    attendance_pct: float
    is_projected: bool

class SubjectTrajectoryItem(BaseModel):
    subject_code: str
    subject_name: str
    student_marks_pct: float
    student_attendance_pct: float
    cohort_avg: float
    benchmark: float = 75.0
    trend: str  # "Improving", "Declining", "Stable"

# ----------------- Mentor Meeting Schemas -----------------

class MentorMeetingCreateRequest(BaseModel):
    student_id: int
    meeting_date: datetime
    meeting_type: str = Field("In Person", description="In Person, Online, Phone")
    duration_minutes: int = Field(30, ge=5, le=240)
    discussion_summary: str = Field(..., min_length=5)
    academic_concerns: Optional[str] = None
    agreed_actions: Optional[str] = None
    next_followup_date: Optional[datetime] = None
    meeting_status: str = Field("completed", description="completed, scheduled, cancelled")

class MentorMeetingUpdateRequest(BaseModel):
    discussion_summary: Optional[str] = None
    academic_concerns: Optional[str] = None
    agreed_actions: Optional[str] = None
    next_followup_date: Optional[datetime] = None
    meeting_status: Optional[str] = None

class MentorMeetingResponse(BaseModel):
    id: int
    mentor_id: int
    mentor_name: str
    faculty_code: str
    student_id: int
    student_name: str
    registration_number: str
    section: str
    meeting_date: datetime
    meeting_type: str
    duration_minutes: int
    discussion_summary: str
    academic_concerns: Optional[str] = None
    agreed_actions: Optional[str] = None
    next_followup_date: Optional[datetime] = None
    meeting_status: str
    created_at: datetime
    updated_at: datetime
    followup_status: Optional[str] = None  # "Upcoming", "Overdue", "Completed", "None"

    concern_flag: bool = False

class StudentCohortComparison(BaseModel):
    student_assessment_avg: float
    cohort_assessment_avg: float
    student_attendance_pct: float
    institutional_attendance_goal: float = 85.0
    student_assignment_pct: float
    cohort_assignment_avg: float
    sample_size_label: str = "Allocated Mentee Cohort (N=10)"

class StudentTrajectoryResponse(BaseModel):
    student_id: int
    name: str
    registration_number: str
    academic_status: str
    trend_classification: str  # "Improving", "Declining", "Stable", "Insufficient Data"
    trend_slope: float
    method_documentation: str
    weekly_trajectory: List[WeeklyTrajectoryPoint]
    subject_trajectories: List[SubjectTrajectoryItem]
    comparison: StudentCohortComparison

class TaskRecommendationItem(BaseModel):
    id: str
    student_id: int
    student_name: str
    registration_number: str
    section: str
    course_code: str
    course_name: str
    trigger_reason: str
    evidence: Dict[str, Any]
    recommended_title: str
    recommended_description: str
    priority: str  # High, Medium, Low
    suggested_frequency: str
    suggested_duration: str
    suggested_deadline: str
    explanation: str

class RecommendationApproveRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class RecommendationDismissRequest(BaseModel):
    justification: str
