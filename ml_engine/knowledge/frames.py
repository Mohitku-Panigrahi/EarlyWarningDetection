from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Frame:
    """Base class for Knowledge Representation Frames (Minsky's Frame Theory)."""
    frame_id: str
    frame_type: str
    slots: Dict[str, Any] = field(default_factory=dict)

    def get_slot(self, slot_name: str, default: Any = None) -> Any:
        return self.slots.get(slot_name, default)

    def set_slot(self, slot_name: str, value: Any):
        self.slots[slot_name] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "frame_type": self.frame_type,
            "slots": self.slots,
        }

@dataclass
class StudentFrame(Frame):
    def __init__(
        self,
        student_id: str,
        name: str,
        section: str,
        mentor_id: str,
        cgpa: float,
        attendance_pct: float,
        risk_status: str = "ON TRACK",
        enrolled_subjects: Optional[List[str]] = None,
    ):
        super().__init__(
            frame_id=f"STUDENT_{student_id}",
            frame_type="Student",
            slots={
                "registration_number": student_id,
                "full_name": name,
                "section": section,
                "mentor_id": mentor_id,
                "cgpa": cgpa,
                "attendance_pct": attendance_pct,
                "risk_status": risk_status,
                "enrolled_subjects": enrolled_subjects or [],
            },
        )

@dataclass
class SubjectFrame(Frame):
    def __init__(
        self,
        subject_code: str,
        title: str,
        delivered_lectures: int,
        faculty_id: str,
        is_core: bool = True,
    ):
        super().__init__(
            frame_id=f"SUBJECT_{subject_code}",
            frame_type="Subject",
            slots={
                "subject_code": subject_code,
                "title": title,
                "delivered_lectures": delivered_lectures,
                "faculty_id": faculty_id,
                "is_core": is_core,
            },
        )

@dataclass
class AssessmentFrame(Frame):
    def __init__(
        self,
        assessment_id: str,
        subject_code: str,
        assessment_type: str,
        max_marks: float,
        weightage_pct: float,
    ):
        super().__init__(
            frame_id=f"ASSESSMENT_{assessment_id}",
            frame_type="Assessment",
            slots={
                "assessment_id": assessment_id,
                "subject_code": subject_code,
                "assessment_type": assessment_type,
                "max_marks": max_marks,
                "weightage_pct": weightage_pct,
            },
        )

@dataclass
class AttendanceFrame(Frame):
    def __init__(
        self,
        student_id: str,
        subject_code: str,
        attended: int,
        delivered: int,
        duty_leave: int = 0,
    ):
        pct = round(100.0 * (attended + duty_leave) / max(1, delivered), 1)
        super().__init__(
            frame_id=f"ATTENDANCE_{student_id}_{subject_code}",
            frame_type="Attendance",
            slots={
                "student_id": student_id,
                "subject_code": subject_code,
                "attended": attended,
                "delivered": delivered,
                "duty_leave": duty_leave,
                "calculated_pct": pct,
                "below_statutory_threshold": pct < 75.0,
            },
        )

@dataclass
class InterventionFrame(Frame):
    def __init__(
        self,
        intervention_id: str,
        student_id: str,
        mentor_id: str,
        intervention_type: str,
        priority: str,
        status: str = "proposed",
    ):
        super().__init__(
            frame_id=f"INTERVENTION_{intervention_id}",
            frame_type="Intervention",
            slots={
                "intervention_id": intervention_id,
                "student_id": student_id,
                "mentor_id": mentor_id,
                "intervention_type": intervention_type,
                "priority": priority,
                "status": status,
            },
        )

@dataclass
class MentorFrame(Frame):
    def __init__(
        self,
        mentor_id: str,
        name: str,
        department: str,
        max_caseload: int = 15,
        assigned_mentees: Optional[List[str]] = None,
    ):
        mentees = assigned_mentees or []
        super().__init__(
            frame_id=f"MENTOR_{mentor_id}",
            frame_type="Mentor",
            slots={
                "mentor_id": mentor_id,
                "name": name,
                "department": department,
                "max_caseload": max_caseload,
                "assigned_mentees": mentees,
                "caseload_count": len(mentees),
                "is_overloaded": len(mentees) > max_caseload,
            },
        )
