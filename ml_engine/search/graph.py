from typing import Dict, List, Optional, Any
from ml_engine.search.state import AcademicPlanningState
from ml_engine.search.transitions import AcademicTransition

class InterventionStateSpace:
    """
    Formal state-space representation for academic intervention planning.
    Demonstrates CSE276 Unit II State-Space & Search Algorithms.
    """

    def __init__(self):
        self.states: Dict[str, AcademicPlanningState] = {}
        self.transitions: List[AcademicTransition] = []
        self._adjacency: Dict[str, List[AcademicTransition]] = {}
        self._heuristic_to_goal: Dict[str, float] = {}
        self._build_default_state_space()

    def _build_default_state_space(self):
        # 1. Academic Planning States
        state_defs = [
            AcademicPlanningState(
                state_id="INITIAL_REVIEW",
                name="Initial Academic Review",
                stage_category="Detection",
                description="Student shows early friction indicators (attendance < 75% or test drop).",
                estimated_workload_hours=0.5,
                urgency_level="MEDIUM",
            ),
            AcademicPlanningState(
                state_id="MENTOR_MEETING",
                name="One-on-One Mentor Meeting",
                stage_category="Diagnostics",
                description="Mentor conducts diagnostic interview to identify academic/personal hurdles.",
                estimated_workload_hours=1.0,
                urgency_level="HIGH",
            ),
            AcademicPlanningState(
                state_id="ATTENDANCE_SUPPORT",
                name="Attendance Recovery Plan",
                stage_category="Action",
                description="Structured attendance tracking with weekly mentor check-ins.",
                estimated_workload_hours=2.0,
                urgency_level="HIGH",
            ),
            AcademicPlanningState(
                state_id="SUBJECT_TUTORING",
                name="Remedial Subject Tutoring",
                stage_category="Action",
                description="Assigned peer or TA tutoring in weak subject (e.g. MTH401, CSE205).",
                estimated_workload_hours=4.0,
                urgency_level="MEDIUM",
            ),
            AcademicPlanningState(
                state_id="ASSIGNMENT_PLANNING",
                name="Assignment Pacing Support",
                stage_category="Action",
                description="Structured submission schedule for pending continuous evaluation components.",
                estimated_workload_hours=1.5,
                urgency_level="LOW",
            ),
            AcademicPlanningState(
                state_id="FACULTY_REFERRAL",
                name="Course Teacher Referral",
                stage_category="Action",
                description="Formal referral to the specific course instructor for conceptual doubts.",
                estimated_workload_hours=1.0,
                urgency_level="MEDIUM",
            ),
            AcademicPlanningState(
                state_id="FOLLOW_UP_REVIEW",
                name="Progress Follow-up Review",
                stage_category="Evaluation",
                description="Bi-weekly checkpoint to evaluate student adherence and academic trajectory.",
                estimated_workload_hours=0.5,
                urgency_level="LOW",
            ),
            AcademicPlanningState(
                state_id="PLAN_COMPLETED",
                name="Intervention Plan Completed",
                stage_category="Resolution",
                description="Academic metrics stabilized; intervention successfully documented and closed.",
                estimated_workload_hours=0.0,
                urgency_level="LOW",
            ),
        ]

        for s in state_defs:
            self.states[s.state_id] = s
            self._adjacency[s.state_id] = []

        # 2. Pedagogical Transitions (source -> dest, action, cost, heuristic_weight)
        # Cost represents mentor/student effort hours; heuristic_weight represents estimated distance to goal
        trans_defs = [
            AcademicTransition("T01", "INITIAL_REVIEW", "MENTOR_MEETING", "Schedule Mentoring Session", 1.0, 3.0,
                               ["Student flagged by Monitor component"], "Direct diagnostic conversation with assigned mentor."),
            AcademicTransition("T02", "INITIAL_REVIEW", "ATTENDANCE_SUPPORT", "Initiate Attendance Tracking", 1.5, 4.0,
                               ["Attendance < 75%"], "Immediate attendance monitoring before formal interview."),
            AcademicTransition("T03", "MENTOR_MEETING", "ATTENDANCE_SUPPORT", "Authorize Attendance Plan", 1.0, 3.0,
                               ["Attendance deficit confirmed in interview"], "Formulate 3-week attendance recovery roadmap."),
            AcademicTransition("T04", "MENTOR_MEETING", "SUBJECT_TUTORING", "Assign Subject Tutor", 2.0, 2.5,
                               ["Assessment score drop in core course"], "Connect student with department teaching assistant."),
            AcademicTransition("T05", "MENTOR_MEETING", "ASSIGNMENT_PLANNING", "Create Assignment Calendar", 1.0, 2.5,
                               ["Pending assignments >= 2"], "Establish milestone deadlines for backlog assignments."),
            AcademicTransition("T06", "MENTOR_MEETING", "FACULTY_REFERRAL", "Refer to Course Faculty", 1.0, 2.8,
                               ["Conceptual roadblock identified"], "Refer to course teacher for specialized consultation."),
            AcademicTransition("T07", "ATTENDANCE_SUPPORT", "FOLLOW_UP_REVIEW", "Log Attendance Milestone", 1.5, 1.5,
                               ["Attendance checked for 2 consecutive weeks"], "Review attendance improvement trajectory."),
            AcademicTransition("T08", "SUBJECT_TUTORING", "FOLLOW_UP_REVIEW", "Assess Tutorial Outcomes", 2.0, 1.0,
                               ["Completed at least 3 tutoring sessions"], "Check performance on subsequent quiz/test."),
            AcademicTransition("T09", "ASSIGNMENT_PLANNING", "FOLLOW_UP_REVIEW", "Verify Submissions", 1.0, 1.0,
                               ["All backlog tasks submitted"], "Confirm submission on LMS/SIS."),
            AcademicTransition("T10", "FACULTY_REFERRAL", "FOLLOW_UP_REVIEW", "Collect Faculty Feedback", 1.0, 1.2,
                               ["Faculty consultation conducted"], "Teacher provides evaluation notes to mentor."),
            AcademicTransition("T11", "FOLLOW_UP_REVIEW", "PLAN_COMPLETED", "Finalize & Close Plan", 0.5, 0.0,
                               ["Academic indicators returned to ON TRACK"], "Intervention recorded and closed in audit log."),
            AcademicTransition("T12", "FOLLOW_UP_REVIEW", "MENTOR_MEETING", "Re-convene Mentor Meeting", 1.0, 3.5,
                               ["Insufficient progress observed"], "Secondary review to revise action strategies."),
        ]

        for t in trans_defs:
            self.transitions.append(t)
            self._adjacency[t.source_state].append(t)

        # 3. Admissible Heuristic Values h(n) towards PLAN_COMPLETED
        # Admissible: never overestimates actual minimal remaining cost to PLAN_COMPLETED
        # Minimal remaining paths:
        # PLAN_COMPLETED: 0.0
        # FOLLOW_UP_REVIEW: 0.5 (T11: 0.5)
        # ASSIGNMENT_PLANNING: 1.5 (T09: 1.0 + T11: 0.5)
        # FACULTY_REFERRAL: 1.5 (T10: 1.0 + T11: 0.5)
        # ATTENDANCE_SUPPORT: 2.0 (T07: 1.5 + T11: 0.5)
        # SUBJECT_TUTORING: 2.5 (T08: 2.0 + T11: 0.5)
        # MENTOR_MEETING: 2.0 (T05: 1.0 + T09: 1.0 + T11: 0.5 = 2.5) -> set to 2.0 for admissibility
        # INITIAL_REVIEW: 3.0 (T01: 1.0 + 2.0 = 3.0)
        self._heuristic_to_goal = {
            "PLAN_COMPLETED": 0.0,
            "FOLLOW_UP_REVIEW": 0.5,
            "ASSIGNMENT_PLANNING": 1.5,
            "FACULTY_REFERRAL": 1.5,
            "ATTENDANCE_SUPPORT": 2.0,
            "SUBJECT_TUTORING": 2.5,
            "MENTOR_MEETING": 2.0,
            "INITIAL_REVIEW": 3.0,
        }

    def get_neighbors(self, state_id: str) -> List[AcademicTransition]:
        return self._adjacency.get(state_id, [])

    def get_heuristic(self, state_id: str, goal_id: str = "PLAN_COMPLETED") -> float:
        """Returns admissible heuristic h(n). Defaults to pre-computed distance to PLAN_COMPLETED."""
        if state_id == goal_id:
            return 0.0
        return self._heuristic_to_goal.get(state_id, 1.0)

    def to_graph_data(self) -> Dict[str, Any]:
        """Serializes state-space graph for frontend visualization in Research Lab."""
        return {
            "states": [s.to_dict() for s in self.states.values()],
            "transitions": [t.to_dict() for t in self.transitions],
            "heuristics": self._heuristic_to_goal,
        }
