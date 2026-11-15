from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class AcademicPlanningState:
    """
    Immutable representation of an intervention planning condition.
    States represent pedagogical and support workflow milestones, NOT arbitrary graph nodes.
    """
    state_id: str
    name: str
    stage_category: str
    description: str
    estimated_workload_hours: float
    urgency_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "name": self.name,
            "stage_category": self.stage_category,
            "description": self.description,
            "estimated_workload_hours": self.estimated_workload_hours,
            "urgency_level": self.urgency_level,
        }
