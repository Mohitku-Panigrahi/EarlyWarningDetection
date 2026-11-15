from dataclasses import dataclass, field
from typing import Dict, Any, List, Set

@dataclass
class SemanticNode:
    id: str
    label: str
    category: str  # "Entity", "Concept", "Indicator", "Action", "Faculty"
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "category": self.category,
            "attributes": self.attributes,
        }

@dataclass
class SemanticEdge:
    source: str
    target: str
    relation: str  # "is-a", "enrolled-in", "advised-by", "exhibits", "triggers", "resolved-by", "teaches"
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
        }

class AcademicSemanticNetwork:
    """
    Semantic Network representing conceptual academic knowledge in LPU-RISK-01.
    Demonstrates CSE276 Unit II Semantic Networks & Associative Nets.
    """

    def __init__(self):
        self.nodes: Dict[str, SemanticNode] = {}
        self.edges: List[SemanticEdge] = []
        self._build_default_ontology()

    def add_node(self, node: SemanticNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: SemanticEdge):
        self.edges.append(edge)

    def _build_default_ontology(self):
        # 1. Base Taxonomic Concepts
        self.add_node(SemanticNode("UniversityMember", "University Member", "Concept"))
        self.add_node(SemanticNode("Student", "Student", "Concept"))
        self.add_node(SemanticNode("Faculty", "Faculty", "Concept"))
        self.add_node(SemanticNode("CourseTeacher", "Course Teacher", "Concept"))
        self.add_node(SemanticNode("Mentor", "Faculty Mentor", "Concept"))
        self.add_node(SemanticNode("Subject", "Academic Subject", "Concept"))
        self.add_node(SemanticNode("EarlyWarningSignal", "Early-Warning Signal", "Concept"))
        self.add_node(SemanticNode("Intervention", "Pedagogical Intervention", "Concept"))

        # Hierarchy edges
        self.add_edge(SemanticEdge("Student", "UniversityMember", "is-a"))
        self.add_edge(SemanticEdge("Faculty", "UniversityMember", "is-a"))
        self.add_edge(SemanticEdge("CourseTeacher", "Faculty", "is-a"))
        self.add_edge(SemanticEdge("Mentor", "Faculty", "is-a"))

        # 2. Key Academic Subjects
        self.add_node(SemanticNode("CSE276", "AI Foundations (CSE276)", "Entity", {"credits": 4}))
        self.add_node(SemanticNode("MTH401", "Discrete Mathematics (MTH401)", "Entity", {"credits": 4}))
        self.add_node(SemanticNode("CSE205", "Data Structures & Algos (CSE205)", "Entity", {"credits": 4}))
        self.add_edge(SemanticEdge("CSE276", "Subject", "is-a"))
        self.add_edge(SemanticEdge("MTH401", "Subject", "is-a"))
        self.add_edge(SemanticEdge("CSE205", "Subject", "is-a"))

        # 3. Indicators & Signals
        self.add_node(SemanticNode("LowAttendanceSignal", "Attendance Deficit (<75%)", "Indicator"))
        self.add_node(SemanticNode("AssessmentDropSignal", "Assessment Score Drop (>=10%)", "Indicator"))
        self.add_node(SemanticNode("MissingTaskSignal", "Overdue Assignments (>=2)", "Indicator"))
        self.add_edge(SemanticEdge("LowAttendanceSignal", "EarlyWarningSignal", "is-a"))
        self.add_edge(SemanticEdge("AssessmentDropSignal", "EarlyWarningSignal", "is-a"))
        self.add_edge(SemanticEdge("MissingTaskSignal", "EarlyWarningSignal", "is-a"))

        # 4. Interventions
        self.add_node(SemanticNode("AttendancePlan", "Attendance Recovery Plan", "Action"))
        self.add_node(SemanticNode("SubjectTutoringPlan", "Subject Peer Tutoring", "Action"))
        self.add_node(SemanticNode("AssignmentPlan", "Assignment Milestone Plan", "Action"))
        self.add_node(SemanticNode("MentorMeeting", "Diagnostic Mentor Interview", "Action"))
        self.add_edge(SemanticEdge("AttendancePlan", "Intervention", "is-a"))
        self.add_edge(SemanticEdge("SubjectTutoringPlan", "Intervention", "is-a"))
        self.add_edge(SemanticEdge("AssignmentPlan", "Intervention", "is-a"))
        self.add_edge(SemanticEdge("MentorMeeting", "Intervention", "is-a"))

        # 5. Associative & Resolution Links
        self.add_edge(SemanticEdge("LowAttendanceSignal", "AttendancePlan", "resolved-by"))
        self.add_edge(SemanticEdge("AssessmentDropSignal", "SubjectTutoringPlan", "resolved-by"))
        self.add_edge(SemanticEdge("MissingTaskSignal", "AssignmentPlan", "resolved-by"))
        self.add_edge(SemanticEdge("EarlyWarningSignal", "MentorMeeting", "requires-oversight"))

    def instantiate_student(
        self,
        student_id: str,
        name: str,
        mentor_id: str,
        active_signals: List[str],
    ) -> Dict[str, Any]:
        """Instantiates a dynamic student node with its relational edges."""
        s_node_id = f"Student_{student_id}"
        self.add_node(SemanticNode(s_node_id, f"{name} ({student_id})", "Entity"))
        self.add_edge(SemanticEdge(s_node_id, "Student", "is-a"))
        self.add_edge(SemanticEdge(s_node_id, f"Mentor_{mentor_id}", "advised-by"))

        for sig in active_signals:
            if sig in self.nodes:
                self.add_edge(SemanticEdge(s_node_id, sig, "exhibits"))

        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }
