from typing import Dict, Any, List

class Predicate:
    """Base class for First-Order Logic Predicates."""
    name: str

    def evaluate(self, *args, **kwargs) -> bool:
        raise NotImplementedError

class LowAttendancePredicate(Predicate):
    """LowAttendance(student) <=> student.attendance_pct < threshold (default 75.0%)"""
    name = "LowAttendance"

    @classmethod
    def evaluate(cls, student_data: Dict[str, Any], threshold: float = 75.0) -> bool:
        att = student_data.get("attendance_pct", 100.0)
        return float(att) < threshold

class DecliningPerformancePredicate(Predicate):
    """DecliningPerformance(student) <=> recent_trend < 0 or assessment_drop > threshold"""
    name = "DecliningPerformance"

    @classmethod
    def evaluate(cls, student_data: Dict[str, Any], drop_threshold: float = 10.0) -> bool:
        marks_drop = student_data.get("marks_drop_pct", 0.0)
        trend = student_data.get("recent_trend", "steady")
        return float(marks_drop) >= drop_threshold or trend == "declining"

class IncompleteAssignmentsPredicate(Predicate):
    """IncompleteAssignments(student) <=> missing_submissions >= count_threshold (default 2)"""
    name = "IncompleteAssignments"

    @classmethod
    def evaluate(cls, student_data: Dict[str, Any], count_threshold: int = 2) -> bool:
        missing = student_data.get("missing_count", 0)
        return int(missing) >= count_threshold

class NeedsMentorReviewPredicate(Predicate):
    """
    NeedsMentorReview(student) <=>
    LowAttendance(student) OR (DecliningPerformance(student) AND IncompleteAssignments(student))
    """
    name = "NeedsMentorReview"

    @classmethod
    def evaluate(cls, student_data: Dict[str, Any]) -> bool:
        low_att = LowAttendancePredicate.evaluate(student_data)
        declining = DecliningPerformancePredicate.evaluate(student_data)
        missing = IncompleteAssignmentsPredicate.evaluate(student_data)
        return low_att or (declining and missing)

class StrugglingInSubjectPredicate(Predicate):
    """StrugglingInSubject(student, subject) <=> subject_score < 50.0 OR subject_attendance < 75.0"""
    name = "StrugglingInSubject"

    @classmethod
    def evaluate(
        cls,
        subject_record: Dict[str, Any],
        score_threshold: float = 50.0,
        att_threshold: float = 75.0,
    ) -> bool:
        score = subject_record.get("score_pct", 100.0)
        att = subject_record.get("attendance_pct", 100.0)
        return float(score) < score_threshold or float(att) < att_threshold
