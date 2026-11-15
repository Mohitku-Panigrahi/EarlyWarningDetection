from typing import Dict, Any, List, Callable
from ml_engine.knowledge.predicates import (
    LowAttendancePredicate,
    DecliningPerformancePredicate,
    IncompleteAssignmentsPredicate,
    NeedsMentorReviewPredicate,
)

class FirstOrderEvaluator:
    """
    Evaluator for First-Order Logic (FOL) with Universal (∀) and Existential (∃) Quantifiers.
    Demonstrates CSE276 Unit II First-Order Logic in university cohort governance.
    """

    @staticmethod
    def for_all(
        cohort: List[Dict[str, Any]],
        predicate_fn: Callable[[Dict[str, Any]], bool],
    ) -> Dict[str, Any]:
        """
        Evaluates ∀ s ∈ Cohort: P(s)
        True iff every student in the cohort satisfies P(s).
        """
        counterexamples = []
        for s in cohort:
            if not predicate_fn(s):
                counterexamples.append({
                    "student_id": s.get("student_id") or s.get("registration_number"),
                    "name": s.get("name") or s.get("full_name"),
                })

        satisfied = len(counterexamples) == 0
        return {
            "quantifier": "∀ (Universal)",
            "satisfied": satisfied,
            "cohort_size": len(cohort),
            "counterexamples_count": len(counterexamples),
            "counterexamples": counterexamples[:5],
            "explanation": (
                "Statement holds universally for all cohort members."
                if satisfied
                else f"Statement fails universally; found {len(counterexamples)} counterexample(s)."
            ),
        }

    @staticmethod
    def exists(
        cohort: List[Dict[str, Any]],
        predicate_fn: Callable[[Dict[str, Any]], bool],
    ) -> Dict[str, Any]:
        """
        Evaluates ∃ s ∈ Cohort: P(s)
        True if at least one student in the cohort satisfies P(s).
        """
        witnesses = []
        for s in cohort:
            if predicate_fn(s):
                witnesses.append({
                    "student_id": s.get("student_id") or s.get("registration_number"),
                    "name": s.get("name") or s.get("full_name"),
                })

        satisfied = len(witnesses) > 0
        return {
            "quantifier": "∃ (Existential)",
            "satisfied": satisfied,
            "cohort_size": len(cohort),
            "witnesses_count": len(witnesses),
            "witnesses": witnesses[:5],
            "explanation": (
                f"Statement satisfied existentially; found {len(witnesses)} witness(es)."
                if satisfied
                else "No student in the cohort satisfies the condition."
            ),
        }

    @staticmethod
    def evaluate_cohort_predicates(cohort: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs standard FOL evaluations across an academic section or mentee group."""
        return {
            "exists_needs_review": FirstOrderEvaluator.exists(
                cohort, NeedsMentorReviewPredicate.evaluate
            ),
            "exists_low_attendance": FirstOrderEvaluator.exists(
                cohort, LowAttendancePredicate.evaluate
            ),
            "for_all_acceptable_attendance": FirstOrderEvaluator.for_all(
                cohort, lambda s: not LowAttendancePredicate.evaluate(s)
            ),
            "exists_incomplete_assignments": FirstOrderEvaluator.exists(
                cohort, IncompleteAssignmentsPredicate.evaluate
            ),
        }
