from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ProductionRule:
    rule_id: str
    name: str
    description: str
    suggested_action: str

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class R1_AttendanceThresholdRule(ProductionRule):
    def __init__(self, threshold: float = 75.0):
        super().__init__(
            rule_id="R1",
            name="Attendance Threshold Rule",
            description=f"Triggered when student aggregate attendance falls below {threshold}%.",
            suggested_action="Attendance Recovery Counselling & Daily Monitoring",
        )
        self.threshold = threshold

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        att = float(facts.get("attendance_pct", 100.0))
        triggered = att < self.threshold
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "conditions": f"attendance_pct < {self.threshold}%",
            "observed_value": f"{att:.1f}%",
            "triggered": triggered,
            "suggested_action": self.suggested_action if triggered else "None",
            "explanation": (
                f"Student attendance is {att:.1f}%, which violates the statutory {self.threshold}% university threshold."
                if triggered
                else f"Student attendance ({att:.1f}%) meets or exceeds the {self.threshold}% threshold."
            ),
        }

class R2_AssessmentDeclineRule(ProductionRule):
    def __init__(self, drop_threshold: float = 10.0):
        super().__init__(
            rule_id="R2",
            name="Assessment Trend Decline Rule",
            description=f"Triggered when continuous assessment scores drop by >= {drop_threshold}% across periods.",
            suggested_action="Subject-Specific Peer Tutoring & Doubts Clearing",
        )
        self.drop_threshold = drop_threshold

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        drop = float(facts.get("marks_drop_pct", 0.0))
        trend = facts.get("recent_trend", "steady")
        triggered = drop >= self.drop_threshold or trend == "declining"
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "conditions": f"marks_drop_pct >= {self.drop_threshold}% OR trend == 'declining'",
            "observed_value": f"drop={drop:.1f}%, trend={trend}",
            "triggered": triggered,
            "suggested_action": self.suggested_action if triggered else "None",
            "explanation": (
                f"Continuous assessment performance declined by {drop:.1f}% over the last 2 evaluation cycles."
                if triggered
                else "Assessment trajectory is stable or improving."
            ),
        }

class R3_AssignmentCompletionRule(ProductionRule):
    def __init__(self, missing_threshold: int = 2):
        super().__init__(
            rule_id="R3",
            name="Assignment Completion Rule",
            description=f"Triggered when pending or overdue assignments count >= {missing_threshold}.",
            suggested_action="Assignment Pacing Support & Deadline Extension Review",
        )
        self.missing_threshold = missing_threshold

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        missing = int(facts.get("missing_count", 0))
        triggered = missing >= self.missing_threshold
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "conditions": f"missing_submissions >= {self.missing_threshold}",
            "observed_value": f"{missing} missing",
            "triggered": triggered,
            "suggested_action": self.suggested_action if triggered else "None",
            "explanation": (
                f"Student has accumulated {missing} overdue/missing assignment submissions."
                if triggered
                else f"Assignment completion is acceptable ({missing} missing)."
            ),
        }

class R4_MultiIndicatorSynthesisRule(ProductionRule):
    def __init__(self):
        super().__init__(
            rule_id="R4",
            name="Multi-Indicator Deterioration Synthesis",
            description="Triggered when at least two independent indicators (R1, R2, or R3) show friction.",
            suggested_action="Priority Mentor Diagnostic Meeting & Action Plan",
        )

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        r1 = R1_AttendanceThresholdRule().evaluate(facts)["triggered"]
        r2 = R2_AssessmentDeclineRule().evaluate(facts)["triggered"]
        r3 = R3_AssignmentCompletionRule().evaluate(facts)["triggered"]
        active_count = sum([r1, r2, r3])
        triggered = active_count >= 2

        active_names = []
        if r1: active_names.append("Low Attendance")
        if r2: active_names.append("Declining Scores")
        if r3: active_names.append("Missing Assignments")

        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "conditions": "COUNT(R1, R2, R3) >= 2",
            "observed_value": f"{active_count} of 3 indicators active ({', '.join(active_names) or 'None'})",
            "triggered": triggered,
            "suggested_action": self.suggested_action if triggered else "Routine Monitoring",
            "explanation": (
                f"Compound deterioration detected across {active_count} dimensions ({', '.join(active_names)}). "
                "Requires holistic mentor intervention rather than isolated corrective measures."
                if triggered
                else "Single indicator or no friction detected; compound review threshold not met."
            ),
        }

class ProductionRuleEngine:
    """Production System managing rules R1 through R4 with configurable thresholds."""

    def __init__(
        self,
        att_threshold: float = 75.0,
        marks_drop_threshold: float = 10.0,
        missing_threshold: int = 2,
    ):
        self.rules: List[ProductionRule] = [
            R1_AttendanceThresholdRule(att_threshold),
            R2_AssessmentDeclineRule(marks_drop_threshold),
            R3_AssignmentCompletionRule(missing_threshold),
            R4_MultiIndicatorSynthesisRule(),
        ]

    def evaluate_student(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [rule.evaluate(facts) for rule in self.rules]
