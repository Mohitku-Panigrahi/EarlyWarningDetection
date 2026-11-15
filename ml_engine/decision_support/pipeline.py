from typing import Dict, Any, List, Optional
from ml_engine.rules.rule_engine import EarlyWarningRuleEngine
from ml_engine.explainability.feature_attribution import FeatureAttributionExplainer
from ml_engine.explainability.counterfactuals import CounterfactualSimulator, TransparentBayesianUpdater

class AcademicMonitorComponent:
    """Component 1: Ingests and validates academic telemetry."""
    @staticmethod
    def extract_indicators(
        attendance_pct: float,
        recent_marks_pct: float,
        missing_count: int,
        sgpa: float = 7.5,
    ) -> Dict[str, float]:
        return {
            "attendance_pct": max(0.0, min(100.0, float(attendance_pct))),
            "recent_marks_pct": max(0.0, min(100.0, float(recent_marks_pct))),
            "missing_count": max(0, int(missing_count)),
            "sgpa": max(0.0, min(10.0, float(sgpa))),
        }

class AcademicRiskComponent:
    """Component 2: Computes risk probability and status classification."""
    def __init__(self, threshold: float = 0.40):
        self.threshold = threshold

    def score(
        self,
        indicators: Dict[str, float],
        prob_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        if prob_override is not None:
            prob = prob_override
        else:
            # Deterministic calculation formula for demo baseline
            att_factor = max(0.0, (85.0 - indicators["attendance_pct"]) * 0.012)
            marks_factor = max(0.0, (75.0 - indicators["recent_marks_pct"]) * 0.008)
            sub_factor = indicators["missing_count"] * 0.08
            prob = max(0.05, min(0.95, 0.15 + att_factor + marks_factor + sub_factor))

        if prob >= 0.55 or indicators["attendance_pct"] < 70.0:
            status = "NEEDS REVIEW"
        elif prob >= self.threshold or indicators["attendance_pct"] < 75.0 or indicators["missing_count"] >= 2:
            status = "WATCH"
        else:
            status = "ON TRACK"

        return {
            "probability": round(float(prob), 4),
            "threshold": self.threshold,
            "status": status,
        }

class AcademicExplainerComponent:
    """Component 3: Generates transparent SHAP, rule trace, counterfactual, and Bayesian outputs."""
    def __init__(self):
        self.rule_engine = EarlyWarningRuleEngine()
        self.attribution = FeatureAttributionExplainer()
        self.bayesian = TransparentBayesianUpdater()

    def explain(
        self,
        indicators: Dict[str, float],
        risk_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        # 1. Rules
        rules = self.rule_engine.evaluate(
            attendance_pct=indicators["attendance_pct"],
            recent_marks_pct=indicators["recent_marks_pct"],
            missing_submissions=int(indicators["missing_count"]),
        )
        rules_fired = [r.to_dict() for r in rules]

        # 2. Counterfactual
        cf = CounterfactualSimulator.simulate_recovery(
            current_prob=risk_result["probability"],
            attendance_pct=indicators["attendance_pct"],
            missing_count=int(indicators["missing_count"]),
        )

        # 3. Bayesian
        bayes = self.bayesian.update(
            has_low_attendance=indicators["attendance_pct"] < 75.0,
            has_low_marks=indicators["recent_marks_pct"] < 65.0,
            has_overdue_work=indicators["missing_count"] >= 2,
        )

        return {
            "rules_fired": rules_fired,
            "counterfactual": cf,
            "bayesian": bayes,
        }

class AcademicPlannerComponent:
    """Component 4: Proposes targeted interventions for human mentor review."""
    @staticmethod
    def plan(
        rules_fired: List[Dict[str, Any]],
        student_id: int,
    ) -> List[Dict[str, Any]]:
        proposals = []
        for r in rules_fired:
            proposals.append({
                "student_id": student_id,
                "playbook_id": r.get("suggested_playbook_id", "PB11"),
                "intervention_type": "Subject Tutoring & Practice" if r["rule_id"] == "R2" else "Attendance Recovery",
                "recommendation": r["suggested_action"],
                "reason": r["details"],
                "priority": r["severity"],
                "requires_human_approval": True,
            })
        return proposals
