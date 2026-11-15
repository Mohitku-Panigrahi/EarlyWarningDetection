from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchExecuteRequest(BaseModel):
    algorithm: str = Field(default="A*", description="Algorithm name: BFS, DFS, Best-First, Hill Climbing, A*")
    start_state: str = Field(default="INITIAL_REVIEW", description="Initial state ID")
    goal_state: str = Field(default="PLAN_COMPLETED", description="Goal state ID")

class SearchExecuteResponse(BaseModel):
    algorithm: str
    start_state: str
    goal_state: str
    path: List[str]
    visited_nodes: List[str]
    expansion_order: List[str]
    nodes_expanded: int
    path_cost: float
    step_count: int
    duration_ms: float
    completion_status: str
    explanation: str
    step_evaluations: Optional[List[Dict[str, Any]]] = None
    node_evaluations: Optional[List[Dict[str, Any]]] = None

class SearchCompareResponse(BaseModel):
    start_state: str
    goal_state: str
    comparison: List[Dict[str, Any]]
    graph_summary: Dict[str, Any]

class KnowledgeEvaluateRequest(BaseModel):
    student_id: Optional[str] = "12511001"
    name: Optional[str] = "Aarav Sharma"
    attendance_pct: float = Field(default=82.0, ge=0.0, le=100.0)
    marks_drop_pct: float = Field(default=6.0, ge=0.0, le=100.0)
    missing_count: int = Field(default=1, ge=0)
    recent_trend: str = Field(default="declining")

class KnowledgeEvaluateResponse(BaseModel):
    student_frame: Dict[str, Any]
    predicates: Dict[str, bool]
    production_rules: List[Dict[str, Any]]
    propositional_reasoning: Dict[str, Any]
    active_rules_count: int

class BayesianUpdateRequest(BaseModel):
    has_low_attendance: bool = True
    has_low_marks: bool = True
    has_overdue_work: bool = False
    prior: Optional[float] = Field(default=0.22, ge=0.001, le=0.999)

class BayesianUpdateResponse(BaseModel):
    hypothesis: str
    prior: float
    prior_complement: float
    evidence: str
    likelihood_P_E_given_H: float
    likelihood_P_E_given_not_H: float
    marginal_likelihood_P_E: float
    likelihood_ratio: float
    posterior: float
    posterior_complement: float
    is_normalized: bool
    calculation_formula: str
    assumptions: str
