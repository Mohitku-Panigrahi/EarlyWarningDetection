import json
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple
import numpy as np
import random
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.academic import Section, Mentor, Student, Subject
from backend.app.models.performance import (
    StudentSubjectPerformance,
    AcademicRecord,
    WeeklyAcademicMetric,
    WeeklyAttendance,
    WeeklyActivity,
)
from backend.app.models.assessment import Assessment, StudentAssessment
from backend.app.models.risk import RiskAssessment, ModelRegistry
from backend.app.models.intervention import Playbook, Intervention, MentorDecision, StudentTask
from backend.app.models.system import AuditLog, SystemSetting

# ----------------- SYNTHETIC GENERATION PARAMETERS (MIRRORING LPU) -----------------
SEED = 42
N = 60
WEEKS = 13
TODAY = date(2026, 11, 4)
SEM_START = date(2026, 8, 3)

COURSES = {
    "CSE202": ("OBJECT ORIENTED PROGRAMMING", 46, "F01", 0.00),
    "CSE205": ("DATA STRUCTURES AND ALGORITHMS", 54, "F02", -0.04),
    "CSE276": ("ARTIFICIAL INTELLIGENCE FOUNDATIONS", 33, "F03", 0.00),
    "CSE306": ("COMPUTER NETWORKS", 33, "F04", -0.02),
    "INT335": ("DESIGN THINKING", 18, "F05", 0.05),
    "MTH401": ("DISCRETE MATHEMATICS", 30, "F06", -0.06),
    "PEL134": ("UPPER INTERMEDIATE COMMUNICATION SKILLS-II", 31, "F07", 0.03),
}

FACULTY = [
    ("F01", "Dr. Ritu Malhotra", "course_teacher"),
    ("F02", "Prof. Kabir Anand", "course_teacher"),
    ("F03", "Dr. Sanjay Verma", "course_teacher"),
    ("F04", "Prof. Neha Bajaj", "course_teacher"),
    ("F05", "Prof. Arjun Mehta", "course_teacher"),
    ("F06", "Dr. Sunita Rao", "course_teacher"),
    ("F07", "Prof. Ishita Kapoor", "course_teacher"),
    ("F08", "Dr. Manoj Saini", "mentor"),
    ("F09", "Prof. Leena Thomas", "mentor"),
    ("F10", "Dr. Pawan Chauhan", "mentor"),
    ("F11", "Prof. Farah Siddiqui", "mentor"),
    ("F12", "Dr. Rakesh Nanda", "mentor"),
    ("F13", "Prof. Tanvi Oberoi", "mentor"),
]

SECTIONS = ["K3P25IL", "K3P25IM", "K3P25IN"]
MENTORS_BY_SECTION = {
    "K3P25IL": ["F08", "F09"],
    "K3P25IM": ["F10", "F11"],
    "K3P25IN": ["F12", "F13"],
}

ASSESS = [
    ("PEL134", "Presentation - Individual", "Presentation - Individual", "manual", date(2026, 9, 4), date(2026, 10, 10)),
    ("PEL134", "Interview", "Interview", "manual", date(2026, 9, 17), date(2026, 10, 30)),
    ("MTH401", "Test", "Test 1", "manual", date(2026, 9, 14), date(2026, 9, 21)),
    ("INT335", "Test", "Test", "manual", date(2026, 9, 1), date(2026, 9, 21)),
    ("INT335", "Project", "Project", "manual", date(2026, 8, 30), date(2026, 10, 23)),
    ("INT335", "Assignment - Situation based problem solving", "Assignment", "manual", date(2026, 10, 16), date(2026, 11, 30)),
    ("CSE306", "Test", "Test 1", "manual", date(2026, 10, 1), date(2026, 10, 15)),
    ("CSE276", "Test", "Test 1", "manual", date(2026, 9, 16), date(2026, 9, 17)),
    ("CSE276", "Project", "Project", "online", date(2026, 9, 15), date(2026, 11, 15)),
    ("CSE202", "Test", "Quiz 1", "manual", date(2026, 9, 18), date(2026, 9, 25)),
    ("CSE202", "Assignment", "Assignment 1", "online", date(2026, 10, 5), date(2026, 10, 20)),
    ("CSE205", "Test", "Test 1", "manual", date(2026, 9, 21), date(2026, 9, 28)),
    ("CSE205", "Assignment", "Assignment 1", "online", date(2026, 10, 10), date(2026, 10, 25)),
    ("CSE205", "Test", "Lab Practical", "manual", date(2026, 10, 28), date(2026, 11, 10)),
    ("CSE306", "Assignment", "Assignment 1", "online", date(2026, 10, 22), date(2026, 11, 12)),
    ("MTH401", "Assignment", "Assignment 1", "online", date(2026, 10, 12), date(2026, 10, 28)),
    ("MTH401", "Test", "Test 2", "manual", date(2026, 10, 30), date(2026, 11, 12)),
]
EVAL_CUTOFF = date(2026, 10, 30)

PLAYBOOK_ITEMS = [
    ("PB01", "MTH401", "low_marks", "Unit 1 logic and sets", "Solve 10 problems from Unit 1 (propositional logic, sets, relations) and mark them done.", 40),
    ("PB02", "MTH401", "low_marks", "Proof techniques", "Write 3 proofs by induction and 2 by contradiction; bring doubts to the mentor.", 45),
    ("PB03", "CSE205", "low_marks", "Graph traversal", "Trace BFS and DFS by hand on 3 graphs, then code one in your language.", 45),
    ("PB04", "CSE205", "low_marks", "Complexity", "Solve 5 array/linked-list problems and state the time complexity of each.", 40),
    ("PB05", "CSE276", "low_marks", "PEAS and agents", "Write PEAS descriptions for 3 environments and classify each agent type.", 30),
    ("PB06", "CSE276", "low_marks", "Bayes theorem", "Solve 4 Bayes' theorem numericals with a frequency table.", 30),
    ("PB07", "CSE202", "low_marks", "OOP design", "Implement a small class hierarchy using inheritance and polymorphism.", 45),
    ("PB08", "CSE306", "low_marks", "Subnetting", "Solve 5 subnetting problems and draw the TCP/IP vs OSI layer table.", 40),
    ("PB09", "INT335", "low_marks", "Design thinking", "Prepare an empathy map and a one-line problem statement for your project.", 30),
    ("PB10", "PEL134", "low_marks", "Communication", "Record a 3-minute self-introduction and list 3 things to improve.", 25),
    ("PB11", "ALL", "low_attendance", "Attendance recovery", "Meet your mentor this week and agree an attendance plan for the weakest subject.", 20),
    ("PB12", "ALL", "missing_submission", "Submissions", "Submit the pending assignment within 48 hours or request an extension from the teacher.", 30),
    ("PB13", "ALL", "lms_inactive", "LMS activity", "Log in to the LMS today and complete one pending activity.", 15),
]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Reyansh", "Krishna", "Ishaan", "Kabir", "Rohan", "Dev",
    "Ananya", "Diya", "Ira", "Kavya", "Meera", "Naina", "Riya", "Saanvi", "Tara", "Zoya",
    "Harsh", "Yash", "Manav", "Nikhil", "Pranav", "Rahul", "Siddharth", "Tanmay", "Varun", "Aryan",
    "Isha", "Jiya", "Khushi", "Lavanya", "Mahi", "Nisha", "Pooja", "Roshni", "Sneha", "Trisha",
    "Ibomcha", "Thoiba", "Bijoy", "Subham", "Debasish", "Priyanka", "Ankita", "Gurpreet", "Harpreet", "Simran",
    "Jaskaran", "Amandeep", "Mohammad", "Faiz", "Sara", "Ayesha", "Joseph", "Maria", "Lalit", "Tenzin"
]
LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Gupta", "Mishra", "Patel", "Reddy", "Nair", "Das", "Panda",
    "Sahu", "Behera", "Mohanty", "Kaur", "Gill", "Sandhu", "Khan", "Ansari", "Devi", "Singha",
    "Thapa", "Joshi", "Kulkarni", "Iyer", "Menon", "Chatterjee", "Bose", "Yadav", "Kumar", "Jha",
    "Rana", "Meitei", "Sethi", "Bhatt", "Chopra", "Malik", "Saini", "Tiwari", "Pillai", "Dsouza"
]

ROUTES = ["LPUNEST", "JEE Main", "State CET", "Board Merit"]
RW = [0.45, 0.25, 0.15, 0.15]
BOARDS = ["CBSE", "State Board", "ICSE"]
BW = [0.50, 0.35, 0.15]
MEDIUMS = ["English", "Hindi", "Regional"]
MW = [0.70, 0.20, 0.10]
REGIONS = ["North", "East", "South", "West", "Northeast"]
GW = [0.30, 0.25, 0.15, 0.10, 0.20]

ARCH_PARAMS = {
    "strong": (0.93, 0.82, 0.0, 9.0, 0.97),
    "steady": (0.87, 0.66, 0.0, 7.0, 0.92),
    "struggling": (0.74, 0.44, -0.08, 3.5, 0.65),
    "effort_gap": (0.90, 0.66, 0.0, 7.0, 0.88),
    "disengaged": (0.68, 0.58, -0.20, 2.5, 0.60),
}
DRIFT = {"disengaged": -0.12, "struggling": -0.05, "strong": 0.02}

clip = lambda x, a, b: max(a, min(b, x))

def get_comment(frac: float, status: str) -> str:
    if status == "Not Submitted":
        return "Submission missing. Complete and submit at the earliest."
    if status == "Absent":
        return "Absent for the evaluation. Contact the teacher."
    if frac >= 0.8:
        return "Strong performance. Maintain consistency."
    if frac >= 0.6:
        return "Good attempt. Revise weak concepts and justify answers."
    if frac >= 0.4:
        return "Needs improvement in fundamentals. Practise more problems."
    return "Below expectation. Meet your mentor and follow the practice plan."


class StudentImportService:
    """Service to ingest, validate, and idempotently seed the 60 LPU dummy student records."""

    @classmethod
    def import_dataset(cls, db: Session, force_reload: bool = False) -> Dict[str, Any]:
        """
        Idempotent import pipeline with schema and range validation.
        """
        report = {
            "total_detected": N,
            "imported": 0,
            "updated": 0,
            "rejected": 0,
            "validation_errors": [],
            "missing_values_handled": 0,
            "idempotent": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check existing student count
        existing_students = db.query(Student).count()
        if existing_students >= N and not force_reload:
            report["updated"] = existing_students
            report["idempotent"] = True
            report["status"] = "Idempotent skip: records already present. Set force_reload=True to re-seed."
            return report

        rng = np.random.default_rng(SEED)
        random.seed(SEED)

        try:
            # 1. Seed System Settings
            cls._seed_system_settings(db)

            # 2. Seed Sections
            cls._seed_sections(db)

            # 3. Seed Faculty and Mentors
            faculty_map, mentor_db_map = cls._seed_faculty_and_mentors(db)

            # 4. Seed Subjects (Courses)
            subject_db_map = cls._seed_subjects(db)

            # 5. Seed Playbook
            cls._seed_playbook(db)

            # 6. Seed Assessments
            assessments_meta = cls._seed_assessments(db, subject_db_map)

            # 7. Generate Synthetic Students & Cohort Balancing
            students_data = cls._generate_synthetic_students(rng)

            # 8. Import Students, Academic Records, Attendance, and Scores
            for s in students_data:
                # Validation checks
                if not (12511000 <= int(s["reg"]) <= 12511999):
                    report["rejected"] += 1
                    report["validation_errors"].append(f"Invalid registration number: {s['reg']}")
                    continue
                if not (0.0 <= s["sgpa"] <= 10.0):
                    report["rejected"] += 1
                    report["validation_errors"].append(f"SGPA out of bounds for {s['reg']}: {s['sgpa']}")
                    continue

                # Check or Create User Account
                user = db.query(User).filter_by(username=s["reg"]).first()
                if not user:
                    user = User(
                        username=s["reg"],
                        email=f"{s['reg']}@lpu.in",
                        full_name=s["name"],
                        password_hash=get_password_hash("demo123"),
                        role="student",
                        is_active=True,
                    )
                    db.add(user)
                    db.flush()

                # Check or Create Student Record
                mentor_db_id = mentor_db_map.get(s["mentor"])
                student = db.query(Student).filter_by(registration_number=s["reg"]).first()
                is_new = student is None

                if is_new:
                    student = Student(
                        user_id=user.id,
                        registration_number=s["reg"],
                        department="Computer Science & Engineering",
                        programme="B.Tech Computer Science & Engineering",
                        semester=4,
                        section=s["section"],
                        admission_year=2024,
                        mentor_id=mentor_db_id,
                        academic_status=s["calculated_status"],
                        sem2_sgpa=s["sgpa"],
                        cgpa_band="<6" if s["sgpa"] < 6 else ("6-8" if s["sgpa"] < 8 else "8+"),
                        admission_route=s["route"],
                        schooling_board=s["board"],
                        medium_of_instruction=s["medium"],
                        home_region=s["region"],
                    )
                    db.add(student)
                    db.flush()
                    report["imported"] += 1
                else:
                    student.academic_status = s["calculated_status"]
                    student.mentor_id = mentor_db_id
                    student.sem2_sgpa = s["sgpa"]
                    report["updated"] += 1

                # Academic Record (Sem 2 baseline & Sem 4 current)
                rec = db.query(AcademicRecord).filter_by(student_id=student.id, semester=4).first()
                if not rec:
                    db.add(
                        AcademicRecord(
                            student_id=student.id,
                            semester=4,
                            cgpa=round(s["sgpa"] + rng.normal(0, 0.1), 2),
                            semester_average=round(s["sgpa"] * 0.95, 2),
                            attendance_average=round(s["overall_att_pct"], 1),
                        )
                    )

                # Subject-wise attendance and performance
                for c_code, perf in s["course_perf"].items():
                    subj = subject_db_map.get(c_code)
                    if not subj:
                        continue
                    
                    # Validate attendance constraints
                    delivered = perf["delivered"]
                    attended = perf["attended"]
                    duty_leave = perf["duty_leave"]
                    if attended > delivered or duty_leave > (delivered - attended):
                        report["validation_errors"].append(f"Attendance constraint violated in {c_code} for {s['reg']}")
                        attended = min(attended, delivered)
                    
                    pct = perf["pct"]
                    if not (0 <= pct <= 100):
                        report["validation_errors"].append(f"Attendance percentage out of bounds in {c_code} for {s['reg']}")
                        pct = clip(pct, 0, 100)

                    sp = (
                        db.query(StudentSubjectPerformance)
                        .filter_by(student_id=student.id, subject_id=subj.id)
                        .first()
                    )
                    if not sp:
                        sp = StudentSubjectPerformance(
                            student_id=student.id,
                            subject_id=subj.id,
                            delivered=delivered,
                            attended=attended,
                            duty_leave=duty_leave,
                            first_week_bonus=0,
                            attendance_percentage=pct,
                            internal_marks=perf["internal_marks"],
                            maximum_internal_marks=30.0,
                            assignment_completion=perf["assignment_completion"],
                        )
                        db.add(sp)
                    else:
                        sp.delivered = delivered
                        sp.attended = attended
                        sp.duty_leave = duty_leave
                        sp.attendance_percentage = pct
                        sp.internal_marks = perf["internal_marks"]
                        sp.assignment_completion = perf["assignment_completion"]

                # Weekly Attendance & Activity
                for w_idx in range(WEEKS):
                    w_num = w_idx + 1
                    # Activity (LMS Logins)
                    act = (
                        db.query(WeeklyActivity)
                        .filter_by(student_id=student.id, week_number=w_num)
                        .first()
                    )
                    if not act:
                        db.add(
                            WeeklyActivity(
                                student_id=student.id,
                                week_number=w_num,
                                lms_logins_7d=s["weekly_activity"][w_idx],
                            )
                        )
                    # Weekly Attendance per subject
                    for c_code, w_att in s["weekly_att"][c_code].items() if False else []:
                        pass  # handled in batch below

                for c_code, w_list in s["weekly_att"].items():
                    for w_num, (deliv, att) in enumerate(w_list, 1):
                        watt = (
                            db.query(WeeklyAttendance)
                            .filter_by(student_id=student.id, course_code=c_code, week_number=w_num)
                            .first()
                        )
                        if not watt:
                            db.add(
                                WeeklyAttendance(
                                    student_id=student.id,
                                    course_code=c_code,
                                    week_number=w_num,
                                    delivered=deliv,
                                    attended=att,
                                )
                            )

                # Weekly Aggregate Metrics
                for w_idx in range(WEEKS):
                    w_num = w_idx + 1
                    m = (
                        db.query(WeeklyAcademicMetric)
                        .filter_by(student_id=student.id, week_number=w_num)
                        .first()
                    )
                    if not m:
                        db.add(
                            WeeklyAcademicMetric(
                                student_id=student.id,
                                week_number=w_num,
                                attendance_percentage=s["weekly_agg_att"][w_idx],
                                assessment_score=s["weekly_agg_score"][w_idx],
                                assignment_completion=s["weekly_agg_asg"][w_idx],
                                engagement_metric=float(s["weekly_activity"][w_idx]),
                            )
                        )

                # Student Assessments
                for a_meta in assessments_meta:
                    aid = a_meta["aid"]
                    res = s["assessments"].get(aid, {"marks": None, "status": "Pending", "comment": ""})
                    if res["marks"] is None:
                        report["missing_values_handled"] += 1
                    
                    # Validate mark range
                    if res["marks"] is not None and not (0.0 <= res["marks"] <= a_meta["max_marks"]):
                        report["validation_errors"].append(f"Mark out of range ({res['marks']}) in {aid} for {s['reg']}")
                        res["marks"] = clip(res["marks"], 0.0, a_meta["max_marks"])

                    sa = (
                        db.query(StudentAssessment)
                        .filter_by(student_id=student.id, assessment_id=a_meta["db_id"])
                        .first()
                    )
                    if not sa:
                        db.add(
                            StudentAssessment(
                                student_id=student.id,
                                assessment_id=a_meta["db_id"],
                                marks=res["marks"],
                                status=res["status"],
                                teacher_comment=res["comment"],
                            )
                        )

                # Risk Assessment & Explainability
                ra = (
                    db.query(RiskAssessment)
                    .filter_by(student_id=student.id, assessment_week=6, model_version="v2.4-lpu-demo")
                    .first()
                )
                if not ra:
                    db.add(
                        RiskAssessment(
                            student_id=student.id,
                            model_version="v2.4-lpu-demo",
                            prediction=1 if s["risk_prob"] >= 0.40 else 0,
                            probability=s["risk_prob"],
                            decision_threshold=0.40,
                            status=s["calculated_status"],
                            assessment_week=6,
                            explanation_summary=s["explanation_summary"],
                            shap_json=json.dumps(s["shap_waterfall"]),
                            rules_fired=json.dumps(s["rules_fired"]),
                            counterfactual_json=json.dumps(s["counterfactual"]),
                            bayesian_json=json.dumps(s["bayesian"]),
                        )
                    )

                # Initial Student Tasks (From Playbook)
                cls._seed_student_tasks(db, student, s)

                # Initial Demo Interventions for students with WATCH / NEEDS REVIEW
                if s["calculated_status"] in ("WATCH", "NEEDS REVIEW") and mentor_db_id:
                    cls._seed_student_interventions(db, student, mentor_db_id, s)

            # 9. Seed Model Registry Entry
            cls._seed_model_registry(db)

            # 10. Audit Log for import execution
            admin_user = db.query(User).filter_by(username="admin").first()
            admin_id = admin_user.id if admin_user else None
            db.add(
                AuditLog(
                    user_id=admin_id,
                    actor_role="admin",
                    action="import_demo_dataset",
                    entity_type="system",
                    entity_id="lpu_synthetic_demo",
                    details=f"Imported {report['imported']} records, updated {report['updated']}, missing handled {report['missing_values_handled']}",
                )
            )

            db.commit()
            report["status"] = "Success: 60 LPU dummy student records imported & verified."
            return report

        except Exception as e:
            db.rollback()
            report["status"] = f"Failed with transaction rollback: {str(e)}"
            report["validation_errors"].append(str(e))
            raise e

    # ------------------ HELPER SEED METHODS ------------------

    @classmethod
    def _seed_system_settings(cls, db: Session):
        settings_data = {
            "attendance_threshold_pct": "75",
            "internal_marks_low_pct": "50",
            "missed_assignments_for_medium": "2",
            "lms_inactive_logins_7d": "3",
            "mentor_workload_cap": "10",
            "risk_decision_threshold": "0.40",
            "current_semester": "Semester 4 - Spring (2024-2025)",
            "model_active_version": "v2.4-lpu-demo",
            "demo_mode": "True",
        }
        for k, v in settings_data.items():
            st = db.query(SystemSetting).filter_by(setting_key=k).first()
            if not st:
                db.add(SystemSetting(setting_key=k, setting_value=v))

    @classmethod
    def _seed_sections(cls, db: Session):
        for sec in SECTIONS:
            s_obj = db.query(Section).filter_by(section_code=sec).first()
            if not s_obj:
                db.add(Section(section_code=sec, department="Computer Science & Engineering"))

    @classmethod
    def _seed_faculty_and_mentors(cls, db: Session) -> Tuple[Dict[str, User], Dict[str, int]]:
        faculty_map = {}
        mentor_db_map = {}

        # Also seed Admin user
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@eduvance.edu",
                full_name="Dr. Rajesh Verma (Dean)",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.flush()

        for fac_id, name, role in FACULTY:
            username = f"m{fac_id[1:]}" if role == "mentor" else fac_id.lower()
            user = db.query(User).filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    email=f"{username}@eduvance.edu",
                    full_name=name,
                    password_hash=get_password_hash("mentor123" if role == "mentor" else "faculty123"),
                    role="mentor" if role == "mentor" else "faculty",
                    is_active=True,
                )
                db.add(user)
                db.flush()
            faculty_map[fac_id] = user

            if role == "mentor":
                mentor = db.query(Mentor).filter_by(faculty_code=fac_id).first()
                if not mentor:
                    mentor = Mentor(
                        user_id=user.id,
                        faculty_code=fac_id,
                        department="Computer Science & Engineering",
                        designation="Assoc. Professor" if "Dr." in name else "Assistant Professor",
                        workload_cap=10,
                    )
                    db.add(mentor)
                    db.flush()
                mentor_db_map[fac_id] = mentor.id

        return faculty_map, mentor_db_map

    @classmethod
    def _seed_subjects(cls, db: Session) -> Dict[str, Subject]:
        subject_map = {}
        for code, (title, delivered_total, teacher_id, _) in COURSES.items():
            subj = db.query(Subject).filter_by(subject_code=code).first()
            if not subj:
                subj = Subject(
                    subject_code=code,
                    subject_name=title,
                    semester=4,
                    credits=3 if "COMMUNICATION" not in title else 2,
                    total_lectures=delivered_total,
                    teacher_id=teacher_id,
                )
                db.add(subj)
                db.flush()
            subject_map[code] = subj
        return subject_map

    @classmethod
    def _seed_playbook(cls, db: Session):
        for pid, ccode, trig, topic, task_text, minutes in PLAYBOOK_ITEMS:
            pb = db.query(Playbook).filter_by(id=pid).first()
            if not pb:
                db.add(
                    Playbook(
                        id=pid,
                        course_code=ccode,
                        trigger=trig,
                        topic=topic,
                        task_text=task_text,
                        estimated_minutes=minutes,
                    )
                )

    @classmethod
    def _seed_assessments(cls, db: Session, subject_db_map: Dict[str, Subject]) -> List[Dict[str, Any]]:
        meta_list = []
        for k, (ccode, typ, title, mode, asg_date, due_date) in enumerate(ASSESS, 1):
            aid = f"A{k:02d}"
            ass = db.query(Assessment).filter_by(assessment_code=aid).first()
            if not ass:
                ass = Assessment(
                    assessment_code=aid,
                    course_code=ccode,
                    type=typ,
                    title=title,
                    mode=mode,
                    assigned_date=asg_date,
                    due_date=due_date,
                    max_marks=30.0,
                    faculty_id=COURSES[ccode][2],
                )
                db.add(ass)
                db.flush()
            meta_list.append({
                "aid": aid,
                "db_id": ass.id,
                "course_code": ccode,
                "type": typ,
                "due_date": due_date,
                "max_marks": 30.0,
            })
        return meta_list

    @classmethod
    def _generate_synthetic_students(cls, rng: np.random.Generator) -> List[Dict[str, Any]]:
        names = []
        name_pool = list(FIRST_NAMES)
        random.shuffle(name_pool)
        for i in range(N):
            fn = FIRST_NAMES[i % len(FIRST_NAMES)]
            ln = LAST_NAMES[i % len(LAST_NAMES)]
            names.append(f"{fn} {ln}")

        regs = [str(r) for r in range(12511001, 12511001 + N)]
        archs = ["strong"] * 12 + ["steady"] * 24 + ["struggling"] * 9 + ["effort_gap"] * 9 + ["disengaged"] * 6
        random.shuffle(archs)

        # Pin demo personas
        # index 0: Aarav Sharma (effort_gap)
        archs[0] = "effort_gap"
        names[0] = "Aarav Sharma"
        # index 1: disengaged
        archs[1] = "disengaged"
        # index 2: strong
        archs[2] = "strong"

        students = []
        span = (TODAY - SEM_START).days

        # Weekly delivery distribution per course
        wk_deliv = {}
        for c, (_, tot, _, _) in COURSES.items():
            base, rem = divmod(tot, WEEKS)
            extra = set(random.sample(range(WEEKS), rem))
            wk_deliv[c] = [base + (1 if w in extra else 0) for w in range(WEEKS)]

        for i in range(N):
            a = archs[i]
            ab, sb, slope, lam, psub = ARCH_PARAMS[a]
            medium = str(rng.choice(MEDIUMS, p=MW))

            weak = {}
            if a == "effort_gap":
                pool = ["CSE205", "MTH401", "CSE306", "CSE276"]
                weak_courses = ["MTH401"] if i == 0 else random.sample(pool, random.choice([1, 2]))
                for c in weak_courses:
                    weak[c] = -0.27

            att_base = clip(ab + rng.normal(0, 0.03), 0.50, 0.98)
            skill_base = clip(sb + rng.normal(0, 0.05), 0.25, 0.95)

            skill = {}
            for c, (_, _, _, diff) in COURSES.items():
                med = -0.05 if (c == "PEL134" and medium == "Regional") else (-0.02 if (c == "PEL134" and medium == "Hindi") else 0)
                skill[c] = clip(skill_base + diff + weak.get(c, 0) + med + rng.normal(0, 0.05), 0.10, 0.97)

            sgpa = round(clip(1.0 + 9.5 * skill_base + rng.normal(0, 0.35), 4.0, 9.9), 2)
            section = SECTIONS[i % 3]

            # Attendance simulation
            course_perf = {}
            weekly_att = {}
            total_deliv_all = 0
            total_att_all = 0

            for c, (_, tot, _, _) in COURSES.items():
                ac = clip(att_base + rng.normal(0, 0.03), 0.45, 0.99)
                att_c_tot = 0
                w_list = []
                for w in range(WEEKS):
                    p = clip(ac + slope * (w / (WEEKS - 1) - 0.5) + rng.normal(0, 0.04), 0.15, 1.0)
                    x = int(rng.binomial(wk_deliv[c][w], p))
                    att_c_tot += x
                    w_list.append((wk_deliv[c][w], x))
                weekly_att[c] = w_list

                dl = int(rng.integers(1, 3)) if rng.random() < 0.25 else 0
                dl = min(dl, tot - att_c_tot) if tot - att_c_tot > 0 else 0
                pct = min(100, round(100 * (att_c_tot + dl) / tot))

                # Marks & assignment completion
                c_skill = skill[c]
                internal_m = round(30.0 * clip(c_skill + rng.normal(0, 0.06), 0.2, 0.98) * 2) / 2
                asg_comp = round(clip(psub * 100 + rng.normal(0, 5), 30, 100), 1)

                course_perf[c] = {
                    "delivered": tot,
                    "attended": att_c_tot,
                    "duty_leave": dl,
                    "pct": pct,
                    "internal_marks": internal_m,
                    "assignment_completion": asg_comp,
                }
                total_deliv_all += tot
                total_att_all += (att_c_tot + dl)

            overall_att_pct = min(100.0, round(100.0 * total_att_all / total_deliv_all, 1))

            # Weekly Activity & Aggregate trends
            weekly_activity = []
            weekly_agg_att = []
            weekly_agg_score = []
            weekly_agg_asg = []

            for w in range(WEEKS):
                trend = slope * 3 * (w / (WEEKS - 1) - 0.5)
                lms = int(rng.poisson(max(0.3, lam * (1 + trend))))
                weekly_activity.append(lms)

                # Aggregate attendance for week w
                w_del_sum = sum(weekly_att[c][w][0] for c in COURSES)
                w_att_sum = sum(weekly_att[c][w][1] for c in COURSES)
                w_pct = round(100.0 * w_att_sum / w_del_sum) if w_del_sum > 0 else 80.0
                weekly_agg_att.append(w_pct)

                # Simulated weekly assessment & assignment trend
                w_score = round(clip(skill_base * 100 + trend * 10 + rng.normal(0, 4), 35, 98), 1)
                weekly_agg_score.append(w_score)
                w_asg = round(clip(psub * 100 + trend * 5 + rng.normal(0, 3), 40, 100), 1)
                weekly_agg_asg.append(w_asg)

            # Assessments simulation
            student_assessments = {}
            for k, (c, typ, title, mode, asg_d, due_d) in enumerate(ASSESS, 1):
                aid = f"A{k:02d}"
                # Graded vs Pending flag: first 4 evaluated, rest cutoff
                is_evaluated = due_d <= EVAL_CUTOFF and (k in (1, 2, 3, 8) or (k > 9 and rng.random() < 0.85))
                if not is_evaluated:
                    student_assessments[aid] = {"marks": None, "status": "Pending", "comment": ""}
                    continue

                t = clip((due_d - SEM_START).days / span, 0, 1)
                sk = clip(skill[c] + DRIFT.get(a, 0) * t, 0.05, 0.98)
                is_asg = typ.startswith("Assignment")

                if is_asg and rng.random() > psub:
                    student_assessments[aid] = {"marks": 0.0, "status": "Not Submitted", "comment": get_comment(0, "Not Submitted")}
                elif (not is_asg) and rng.random() < ({"disengaged": 0.08, "struggling": 0.04}.get(a, 0.01)):
                    student_assessments[aid] = {"marks": 0.0, "status": "Absent", "comment": get_comment(0, "Absent")}
                else:
                    fr = clip(sk + rng.normal(0, 0.08), 0.05, 1.0)
                    m = round(30.0 * fr * 2) / 2
                    status = "Present" if not is_asg else "Submitted"
                    student_assessments[aid] = {"marks": m, "status": status, "comment": get_comment(m / 30.0, "ok")}

            # Risk and status calculation
            # Aarav Sharma (i=0) is explicitly set to WATCH with realistic Stitch metrics
            if i == 0:
                calc_status = "WATCH"
                risk_prob = 0.44
                overall_att_pct = 82.0
                explanation_summary = "Mathematics assessment performance has declined (-18% Unit 3). Assignment completion has 2 pending submissions. Attendance is near threshold (82%)."
                
                # Align Aarav's course attendance and marks directly to the Stitch screen
                # Stitch values: MTH401 (64% marks / 78% att), CSE202 (86% marks / 92% att),
                # CSE306/320 (68% marks / 75% att), INT335 (80% marks / 85% att), CSE205 (72% marks / 80% att)
                stitch_align = {
                    "MTH401": (78, 19.0, 70.0),
                    "CSE202": (92, 26.0, 95.0),
                    "CSE205": (80, 21.5, 75.0),
                    "CSE306": (75, 20.5, 70.0),
                    "INT335": (85, 24.0, 85.0),
                    "CSE276": (82, 23.5, 80.0),
                    "PEL134": (84, 23.0, 80.0),
                }
                for c_code, (att_p, m_val, asg_p) in stitch_align.items():
                    tot = course_perf[c_code]["delivered"]
                    new_att = int(round(tot * att_p / 100.0))
                    course_perf[c_code]["attended"] = new_att
                    course_perf[c_code]["duty_leave"] = 0
                    course_perf[c_code]["pct"] = att_p
                    course_perf[c_code]["internal_marks"] = m_val
                    course_perf[c_code]["assignment_completion"] = asg_p

                shap_waterfall = [
                    {"feature": "MTH401 Assessment Drop", "contribution": 0.18, "direction": "positive_risk"},
                    {"feature": "Overdue Assignments (2)", "contribution": 0.12, "direction": "positive_risk"},
                    {"feature": "Attendance (82% vs 85% goal)", "contribution": 0.07, "direction": "positive_risk"},
                    {"feature": "Prior SGPA (7.4)", "contribution": -0.15, "direction": "negative_risk"},
                    {"feature": "CSE202 High Score (86%)", "contribution": -0.08, "direction": "negative_risk"},
                ]
                rules_fired = [
                    {"rule_id": "R1", "rule_name": "Course Marks Dip", "severity": "Medium", "details": "Mathematics performance below 65%"},
                    {"rule_id": "R2", "rule_name": "Pending Submissions", "severity": "Medium", "details": "2 Overdue Assignments in DBMS & Networks"},
                    {"rule_id": "R3", "rule_name": "Attendance Proximity", "severity": "Low", "details": "Overall attendance 82% within 3% of examination clearance limit"},
                ]
                counterfactual = {
                    "scenario": "If attendance improves from 82% to 85% and overdue assignments are submitted",
                    "projected_probability": 0.21,
                    "projected_status": "ON TRACK",
                    "target_actions": ["Submit 2 pending assignments", "Attend next 3 calculus lectures"],
                }
                bayesian = {
                    "prior": 0.22,
                    "evidence": "Observed Math drop + pending submissions",
                    "likelihood_ratio": 2.78,
                    "posterior": 0.44,
                }
            elif a in ("struggling", "disengaged"):
                calc_status = "NEEDS REVIEW" if a == "disengaged" or overall_att_pct < 70 else "WATCH"
                risk_prob = round(float(clip(0.55 + rng.normal(0, 0.1), 0.42, 0.88)), 2)
                explanation_summary = f"Attendance ({overall_att_pct}%) and assessment indicators indicate academic velocity below university benchmarks."
                shap_waterfall = [
                    {"feature": "Overall Attendance Below 75%", "contribution": 0.22, "direction": "positive_risk"},
                    {"feature": "Low Continuous Assessment Scores", "contribution": 0.16, "direction": "positive_risk"},
                    {"feature": "Low LMS Login Activity", "contribution": 0.09, "direction": "positive_risk"},
                ]
                rules_fired = [
                    {"rule_id": "R1", "rule_name": "Low Attendance", "severity": "High", "details": f"Attendance is {overall_att_pct}% (<75%)"},
                    {"rule_id": "R4", "rule_name": "Multiple Indicator Lag", "severity": "High", "details": "Simultaneous attendance and CA deterioration"},
                ]
                counterfactual = {
                    "scenario": "Increasing weekly lecture attendance by 10% and completing remediation tasks",
                    "projected_probability": round(risk_prob - 0.25, 2),
                    "projected_status": "WATCH",
                    "target_actions": ["Meet faculty mentor", "Submit pending assignments"],
                }
                bayesian = {"prior": 0.22, "evidence": "Multiple indicators below threshold", "likelihood_ratio": 3.8, "posterior": risk_prob}
            else:
                calc_status = "ON TRACK"
                risk_prob = round(float(clip(0.12 + rng.normal(0, 0.05), 0.04, 0.32)), 2)
                explanation_summary = "Academic trajectory is consistent and complies with university degree benchmarks."
                shap_waterfall = [
                    {"feature": "Strong Attendance (>85%)", "contribution": -0.20, "direction": "negative_risk"},
                    {"feature": "Consistent Assessment Performance", "contribution": -0.15, "direction": "negative_risk"},
                ]
                rules_fired = []
                counterfactual = {
                    "scenario": "Current trajectory maintains Good Standing status",
                    "projected_probability": risk_prob,
                    "projected_status": "ON TRACK",
                    "target_actions": ["Maintain attendance above 85%"],
                }
                bayesian = {"prior": 0.22, "evidence": "Regular attendance and on-time submissions", "likelihood_ratio": 0.45, "posterior": risk_prob}

            students.append({
                "reg": regs[i],
                "name": names[i],
                "arch": a,
                "section": section,
                "sgpa": sgpa,
                "route": str(rng.choice(ROUTES, p=RW)),
                "board": str(rng.choice(BOARDS, p=BW)),
                "medium": medium,
                "region": str(rng.choice(REGIONS, p=GW)),
                "course_perf": course_perf,
                "weekly_att": weekly_att,
                "weekly_activity": weekly_activity,
                "weekly_agg_att": weekly_agg_att,
                "weekly_agg_score": weekly_agg_score,
                "weekly_agg_asg": weekly_agg_asg,
                "assessments": student_assessments,
                "overall_att_pct": overall_att_pct,
                "calculated_status": calc_status,
                "risk_prob": risk_prob,
                "explanation_summary": explanation_summary,
                "shap_waterfall": shap_waterfall,
                "rules_fired": rules_fired,
                "counterfactual": counterfactual,
                "bayesian": bayesian,
            })

        # Snake-balance mentor allocation (10 mentees per mentor)
        for sec in SECTIONS:
            sec_students = [s for s in students if s["section"] == sec]
            # sort by risk prob so cohorts are balanced
            sec_students.sort(key=lambda x: x["risk_prob"], reverse=True)
            m1, m2 = MENTORS_BY_SECTION[sec]
            for j, s in enumerate(sec_students):
                s["mentor"] = m1 if (j % 4) in (0, 3) else m2
            
            # Explicitly ensure Aarav Sharma (12511001) is assigned to F08 (Dr. Manoj Saini / m08)
            if sec == "K3P25IL":
                aarav_s = next((s for s in sec_students if s["reg"] == "12511001"), None)
                if aarav_s and aarav_s["mentor"] != m1:
                    other = next(s for s in sec_students if s["mentor"] == m1 and s["reg"] != "12511001")
                    aarav_s["mentor"], other["mentor"] = other["mentor"], aarav_s["mentor"]

        return students

    @classmethod
    def _seed_student_tasks(cls, db: Session, student: Student, s_data: Dict[str, Any]):
        """Seed tasks mirroring the Stitch Student Dashboard designs."""
        if s_data["reg"] == "12511001":  # Aarav Sharma
            initial_tasks = [
                ("Unit 3 Differential Calculus Practice", "Mathematics", "High", "pending", datetime.now(timezone.utc) + timedelta(hours=8)),
                ("Submit Relational Schema Normalization Assignment", "DBMS", "High", "pending", datetime.now(timezone.utc) + timedelta(days=1)),
                ("Review Dynamic Memory & Pointers Code Lab", "Programming", "Medium", "pending", datetime.now(timezone.utc) + timedelta(days=2)),
                ("Attend Academic Mentor Discussion with Dr. Rao", "Mentorship", "Medium", "completed", datetime.now(timezone.utc) - timedelta(hours=3)),
            ]
            for title, course, priority, status, due in initial_tasks:
                db.add(
                    StudentTask(
                        student_id=student.id,
                        course_code=course,
                        source="mentor",
                        title=title,
                        priority=priority,
                        status=status,
                        due_date=due,
                        done_at=datetime.now(timezone.utc) if status == "completed" else None,
                    )
                )
        elif s_data["calculated_status"] != "ON TRACK":
            db.add(
                StudentTask(
                    student_id=student.id,
                    course_code="MTH401",
                    source="playbook",
                    playbook_id="PB01",
                    title="Solve 10 problems from Unit 1 (logic, sets) and mark done",
                    priority="High",
                    status="pending",
                    due_date=datetime.now(timezone.utc) + timedelta(days=2),
                )
            )

    @classmethod
    def _seed_student_interventions(cls, db: Session, student: Student, mentor_id: int, s_data: Dict[str, Any]):
        """Seed proposed human-in-the-loop intervention for watch/review students."""
        existing = db.query(Intervention).filter_by(student_id=student.id, mentor_id=mentor_id).first()
        if not existing:
            interv = Intervention(
                student_id=student.id,
                mentor_id=mentor_id,
                playbook_id="PB01" if "MTH401" in s_data["course_perf"] else "PB11",
                intervention_type="Subject Tutoring & Practice",
                recommendation="Recommend 2 weekly 30-min peer-assisted tutoring sessions for Discrete Mathematics and homework review.",
                reason="Calculus assessment drop (-18%) and 2 pending submissions detected by Early-Warning rules.",
                priority="High" if s_data["calculated_status"] == "NEEDS REVIEW" else "Medium",
                status="proposed",
            )
            db.add(interv)

    @classmethod
    def _seed_model_registry(cls, db: Session):
        mr = db.query(ModelRegistry).filter_by(model_version="v2.4-lpu-demo").first()
        if not mr:
            metrics = {
                "recall": 0.84,
                "precision": 0.72,
                "f1": 0.78,
                "f2": 0.81,
                "pr_auc": 0.82,
                "calibration": "Isotonic (cv=5)",
                "note": "Calibrated Random Forest (n_estimators=400, max_depth=8, min_samples_leaf=5)",
            }
            db.add(
                ModelRegistry(
                    model_name="RandomForestClassifier-Calibrated",
                    model_version="v2.4-lpu-demo",
                    dataset_version="synthetic-lpu-v1",
                    metrics_json=json.dumps(metrics),
                    threshold=0.40,
                    status="active",
                )
            )
