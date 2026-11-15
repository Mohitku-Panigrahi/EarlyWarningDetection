from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class AcademicTransition:
    """
    Valid transition between intervention planning states.
    Includes cost, preconditions, and pedagogical explanation.
    """
    transition_id: str
    source_state: str
    dest_state: str
    action: str
    cost: float  # g(n): Resource, time, or cognitive cost
    heuristic_weight: float  # Used by Best-First / A* heuristics
    conditions: List[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "source_state": self.source_state,
            "dest_state": self.dest_state,
            "action": self.action,
            "cost": self.cost,
            "heuristic_weight": self.heuristic_weight,
            "conditions": self.conditions,
            "explanation": self.explanation,
        }
