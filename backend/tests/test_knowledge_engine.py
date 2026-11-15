import pytest
from ml_engine.knowledge.frames import StudentFrame, MentorFrame, SubjectFrame
from ml_engine.knowledge.predicates import (
    LowAttendancePredicate,
    DecliningPerformancePredicate,
    IncompleteAssignmentsPredicate,
    NeedsMentorReviewPredicate,
)
from ml_engine.knowledge.production_rules import ProductionRuleEngine
from ml_engine.knowledge.propositional_logic import (
    PropVar,
    PropAnd,
    PropOr,
    PropImplies,
    PropositionalReasoner,
)
from ml_engine.knowledge.first_order_logic import FirstOrderEvaluator
from ml_engine.knowledge.semantic_network import AcademicSemanticNetwork
from ml_engine.knowledge.knowledge_evaluator import AcademicKnowledgeEvaluator

def test_frames_creation():
    sf = StudentFrame(
        student_id="12511001",
        name="Aarav Sharma",
        section="K3P25IL",
        mentor_id="F08",
        cgpa=8.2,
        attendance_pct=82.0,
    )
    assert sf.frame_type == "Student"
    assert sf.get_slot("registration_number") == "12511001"
    assert sf.get_slot("cgpa") == 8.2

    mf = MentorFrame(
        mentor_id="F08",
        name="Dr. Manoj Saini",
        department="Computer Science & Engineering",
        assigned_mentees=["12511001", "12511002"],
    )
    assert mf.get_slot("caseload_count") == 2
    assert not mf.get_slot("is_overloaded")

def test_predicate_evaluations():
    low_att_student = {"attendance_pct": 68.0, "marks_drop_pct": 5.0, "missing_count": 0}
    assert LowAttendancePredicate.evaluate(low_att_student)
    assert NeedsMentorReviewPredicate.evaluate(low_att_student)

    steady_student = {"attendance_pct": 88.0, "marks_drop_pct": 0.0, "missing_count": 0}
    assert not LowAttendancePredicate.evaluate(steady_student)
    assert not NeedsMentorReviewPredicate.evaluate(steady_student)

    compound_student = {"attendance_pct": 78.0, "marks_drop_pct": 14.0, "missing_count": 3}
    assert not LowAttendancePredicate.evaluate(compound_student)
    assert DecliningPerformancePredicate.evaluate(compound_student)
    assert IncompleteAssignmentsPredicate.evaluate(compound_student)
    assert NeedsMentorReviewPredicate.evaluate(compound_student)

def test_production_rules():
    engine = ProductionRuleEngine()
    facts = {
        "attendance_pct": 69.5,
        "marks_drop_pct": 12.0,
        "missing_count": 3,
        "recent_trend": "declining",
    }
    results = engine.evaluate_student(facts)
    assert len(results) == 4
    
    # R1 (Attendance < 75%), R2 (Drop >= 10%), R3 (Missing >= 2), R4 (>= 2 active)
    triggered_ids = [r["rule_id"] for r in results if r["triggered"]]
    assert "R1" in triggered_ids
    assert "R2" in triggered_ids
    assert "R3" in triggered_ids
    assert "R4" in triggered_ids

def test_propositional_logic_and_truth_table():
    P = PropVar("P")
    Q = PropVar("Q")
    implication = PropImplies(P, Q)

    # Truth table for P -> Q has 4 rows; exactly 3 are True
    tt = PropositionalReasoner.generate_truth_table(implication)
    assert tt["total_rows"] == 4
    assert sum(1 for r in tt["rows"] if r["result"]) == 3
    assert tt["is_satisfiable"]
    assert not tt["is_tautology"]

def test_first_order_quantifiers():
    cohort = [
        {"student_id": "1", "name": "A", "attendance_pct": 85.0},
        {"student_id": "2", "name": "B", "attendance_pct": 70.0},
        {"student_id": "3", "name": "C", "attendance_pct": 90.0},
    ]

    # Exists low attendance -> True (student 2)
    res_exists = FirstOrderEvaluator.exists(cohort, LowAttendancePredicate.evaluate)
    assert res_exists["satisfied"]
    assert res_exists["witnesses_count"] == 1

    # For all acceptable attendance -> False (student 2 fails)
    res_forall = FirstOrderEvaluator.for_all(cohort, lambda s: not LowAttendancePredicate.evaluate(s))
    assert not res_forall["satisfied"]
    assert res_forall["counterexamples_count"] == 1

def test_semantic_network():
    net = AcademicSemanticNetwork()
    data = net.to_dict()
    assert len(data["nodes"]) >= 12
    assert len(data["edges"]) >= 10

def test_knowledge_evaluator():
    evaluator = AcademicKnowledgeEvaluator()
    student = {
        "student_id": "12511001",
        "name": "Aarav Sharma",
        "section": "K3P25IL",
        "attendance_pct": 82.0,
        "marks_drop_pct": 6.0,
        "missing_count": 1,
    }
    report = evaluator.evaluate_student_knowledge(student)
    assert "student_frame" in report
    assert "predicates" in report
    assert "production_rules" in report
    assert "propositional_reasoning" in report
