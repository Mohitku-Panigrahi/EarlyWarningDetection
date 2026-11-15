from typing import List, Dict, Any, Optional

class RuleResult:
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        severity: str,  # High, Medium, Low
        triggered: bool,
        details: str,
        suggested_action: str,
        suggested_playbook_id: str,
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.severity = severity
        self.triggered = triggered
        self.details = details
        self.suggested_action = suggested_action
        self.suggested_playbook_id = suggested_playbook_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "triggered": self.triggered,
            "details": self.details,
            "suggested_action": self.suggested_action,
            "suggested_playbook_id": self.suggested_playbook_id,
        }

class EarlyWarningRuleEngine:
    """
    Transparent, verifiable production heuristics for academic decision support.
    Complements machine learning by capturing deterministic domain rules.
    """

    def __init__(
        self,
        attendance_threshold: float = 75.0,
        marks_cutoff_pct: float = 65.0,
        max_missing_submissions: int = 2,
    ):
        self.attendance_threshold = attendance_threshold
        self.marks_cutoff_pct = marks_cutoff_pct
        self.max_missing_submissions = max_missing_submissions

    def evaluate(
        self,
        attendance_pct: float,
        recent_marks_pct: float,
        missing_submissions: int,
        marks_drop_pct: float = 0.0,
    ) -> List[RuleResult]:
        results = []

        # R1: Attendance Sub-threshold
        if attendance_pct < self.attendance_threshold:
            results.append(
                RuleResult(
                    rule_id="R1",
                    rule_name="Attendance Below Threshold",
                    severity="High" if attendance_pct < 65.0 else "Medium",
                    triggered=True,
                    details=f"Aggregate attendance is {attendance_pct:.1f}% (below institutional {self.attendance_threshold}% target)",
                    suggested_action="Schedule immediate attendance recovery consultation with mentor",
                    suggested_playbook_id="PB11",
                )
            )

        # R2: Continuous Assessment Score Dip
        if recent_marks_pct < self.marks_cutoff_pct or marks_drop_pct >= 10.0:
            results.append(
                RuleResult(
                    rule_id="R2",
                    rule_name="Continuous Evaluation Score Dip",
                    severity="High" if recent_marks_pct < 50.0 else "Medium",
                    triggered=True,
                    details=f"Assessment score is {recent_marks_pct:.1f}% (recent drop: {marks_drop_pct:.1f}%)",
                    suggested_action="Assign focused problem sets from Unit 1 & 2 tutorials",
                    suggested_playbook_id="PB01",
                )
            )

        # R3: Missing or Overdue Submissions
        if missing_submissions >= self.max_missing_submissions:
            results.append(
                RuleResult(
                    rule_id="R3",
                    rule_name="Unsubmitted Coursework Lag",
                    severity="Medium",
                    triggered=True,
                    details=f"{missing_submissions} continuous internal evaluation assignments overdue",
                    suggested_action="Request 48-hour coursework extension and mentor check-in",
                    suggested_playbook_id="PB12",
                )
            )

        # R4: Multi-Indicator Deterioration
        if (attendance_pct < self.attendance_threshold + 5.0) and (recent_marks_pct < self.marks_cutoff_pct):
            results.append(
                RuleResult(
                    rule_id="R4",
                    rule_name="Multiple Indicator Deterioration",
                    severity="High",
                    triggered=True,
                    details="Concurrent attendance proximity and assessment score lag detected",
                    suggested_action="Convene comprehensive mentor-student advisory session",
                    suggested_playbook_id="PB11",
                )
            )

        return results
