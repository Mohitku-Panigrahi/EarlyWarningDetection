from typing import Dict, Any, List, Optional
from ml_engine.knowledge.frames import StudentFrame, MentorFrame, SubjectFrame, AttendanceFrame
from ml_engine.knowledge.predicates import (
    LowAttendancePredicate,
    DecliningPerformancePredicate,
    IncompleteAssignmentsPredicate,
    NeedsMentorReviewPredicate,
    StrugglingInSubjectPredicate,
)
from ml_engine.knowledge.production_rules import ProductionRuleEngine
from ml_engine.knowledge.propositional_logic import (
    PropVar,
    PropNot,
    PropAnd,
    PropOr,
    PropImplies,
    PropositionalReasoner,
)
from ml_engine.knowledge.first_order_logic import FirstOrderEvaluator
from ml_engine.knowledge.semantic_network import AcademicSemanticNetwork

class AcademicKnowledgeEvaluator:
    """
    Unified Knowledge Representation and Reasoning engine for LPU-RISK-01.
    Demonstrates Frames, Predicates, Propositional Logic, FOL, Rules, and Semantic Nets.
    """

    def __init__(self):
        self.rule_engine = ProductionRuleEngine()
        self.semantic_net = AcademicSemanticNetwork()

    def evaluate_student_knowledge(self, student_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the complete knowledge representation analysis on a single student."""
        # 1. Frames Representation
        student_frame = StudentFrame(
            student_id=str(student_dict.get("student_id") or student_dict.get("registration_number", "12511001")),
            name=student_dict.get("name") or student_dict.get("full_name", "Student"),
            section=student_dict.get("section", "K3P25IL"),
            mentor_id=student_dict.get("mentor_id", "F08"),
            cgpa=float(student_dict.get("cgpa", 7.5)),
            attendance_pct=float(student_dict.get("attendance_pct", 80.0)),
            risk_status=student_dict.get("risk_status", "ON TRACK"),
        )

        # 2. Predicate Evaluation
        predicates = {
            "LowAttendance": LowAttendancePredicate.evaluate(student_dict),
            "DecliningPerformance": DecliningPerformancePredicate.evaluate(student_dict),
            "IncompleteAssignments": IncompleteAssignmentsPredicate.evaluate(student_dict),
            "NeedsMentorReview": NeedsMentorReviewPredicate.evaluate(student_dict),
        }

        # 3. Production Rules R1-R4
        rules = self.rule_engine.evaluate_student(student_dict)

        # 4. Propositional Logic Inference
        # Formula: (LowAtt v (Declining ^ Incomplete)) -> NeedsReview
        p_att = PropVar("LowAttendance")
        p_dec = PropVar("DecliningPerformance")
        p_inc = PropVar("IncompleteAssignments")
        p_rev = PropVar("NeedsMentorReview")

        antecedent = PropOr(p_att, PropAnd(p_dec, p_inc))
        implication = PropImplies(antecedent, p_rev)

        prop_eval = PropositionalReasoner.evaluate_expression(
            implication,
            {
                "LowAttendance": predicates["LowAttendance"],
                "DecliningPerformance": predicates["DecliningPerformance"],
                "IncompleteAssignments": predicates["IncompleteAssignments"],
                "NeedsMentorReview": predicates["NeedsMentorReview"],
            },
        )

        return {
            "student_frame": student_frame.to_dict(),
            "predicates": predicates,
            "production_rules": rules,
            "propositional_reasoning": prop_eval,
            "active_rules_count": sum(1 for r in rules if r["triggered"]),
        }

    def get_semantic_network_data(self) -> Dict[str, Any]:
        return self.semantic_net.to_dict()

    def generate_truth_table_demo(self) -> Dict[str, Any]:
        """Generates the truth table for the canonical Early-Warning formula."""
        p_att = PropVar("LowAttendance")
        p_dec = PropVar("DecliningPerformance")
        p_inc = PropVar("IncompleteAssignments")
        p_rev = PropVar("NeedsMentorReview")

        formula = PropImplies(PropOr(p_att, PropAnd(p_dec, p_inc)), p_rev)
        return PropositionalReasoner.generate_truth_table(formula)
