from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AdminKpiData(BaseModel):
    total_monitored_students: int
    on_track_count: int
    on_track_pct: float
    watch_count: int
    watch_pct: float
    needs_review_count: int
    needs_review_pct: float
    pending_mentor_decisions: int

class AdminPrioritySignal(BaseModel):
    id: str
    title: str
    category: str  # ML-Ops Gov, Early-Warning Alert, Mentorship Load, Attendance Anomaly
    severity: str  # urgent, warning, info
    details: str
    action_label: str

class SectionStatusDistribution(BaseModel):
    section: str
    total_students: int
    on_track: int
    watch: int
    needs_review: int

class HeatmapCell(BaseModel):
    section: str
    course_code: str
    avg_attendance: float
    avg_marks: float

class AdminDashboardResponse(BaseModel):
    session_label: str = "2024–2025 Regular • Semester 4 - Spring"
    sync_time: str
    model_version: str = "v2.4-lpu Calibrated"
    system_status: str = "OPERATIONAL"
    kpi: AdminKpiData
    priority_signals: List[AdminPrioritySignal]
    section_distributions: List[SectionStatusDistribution]
    section_subject_heatmap: List[HeatmapCell]

class StudentAdminListItem(BaseModel):
    id: int
    registration_number: str
    name: str
    section: str
    mentor_name: Optional[str] = None
    cgpa: float
    attendance_pct: float
    internal_marks_pct: float
    academic_status: str
    risk_probability: float

class StudentAdminListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    students: List[StudentAdminListItem]

class MentorAnalyticsItem(BaseModel):
    mentor_id: int
    faculty_code: str
    name: str
    department: str
    assigned_mentees: int
    workload_cap: int = 10
    pending_reviews: int
    approved_interventions: int
    completed_interventions: int

class InterventionAnalyticsResponse(BaseModel):
    total_interventions: int
    proposed: int
    approved: int
    rejected: int
    in_progress: int
    completed: int
    by_type: Dict[str, int]

class ModelHealthResponse(BaseModel):
    model_name: str
    model_version: str
    dataset_version: str
    threshold: float
    status: str
    metrics: Dict[str, Any]
    confusion_matrix: Dict[str, int]
    calibration_curve: List[Dict[str, float]]
    recall_by_week: List[Dict[str, Any]]

class FairnessSubgroupMetric(BaseModel):
    subgroup: str
    total_students: int
    at_risk_count: int
    at_risk_rate_pct: float
    mean_attendance_pct: float

class FairnessReportResponse(BaseModel):
    dataset_type: str = "Synthetic Demonstration Telemetry (Seed: 42)"
    evaluation_criteria: str = "Demographic Parity & Subgroup Early-Warning Ratios"
    admission_route: List[FairnessSubgroupMetric]
    schooling_board: List[FairnessSubgroupMetric]
    medium_of_instruction: List[FairnessSubgroupMetric]
    home_region: List[FairnessSubgroupMetric]

class AuditLogItem(BaseModel):
    id: int
    actor_role: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    logs: List[AuditLogItem]

class SystemSettingItem(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime

class SystemSettingsUpdate(BaseModel):
    settings: Dict[str, str]
