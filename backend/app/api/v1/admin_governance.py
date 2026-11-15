import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.academic import Student, Mentor, Section, Subject
from backend.app.models.performance import StudentSubjectPerformance, AcademicRecord, WeeklyAcademicMetric
from backend.app.models.risk import RiskAssessment
from backend.app.models.intervention import Intervention, MentorDecision, StudentTask, MentorMeeting
from backend.app.models.system import AuditLog, SystemSetting
from backend.app.schemas.admin_governance import (
    AttentionQueueItem,
    GovernanceOverviewResponse,
    MentorWorkloadItem,
    StudentDistributionItem,
    MentorDirectoryItem,
    MentorGovernanceProfileResponse,
    StudentMentorRelationshipItem,
    StudentMentorRelationshipResponse,
    StudentGovernanceDetailResponse,
    MeetingAnalyticsResponse,
    FollowupQueueItem,
    AdminInterventionItem,
    AdminInterventionReviewRequest,
)
from backend.app.api.deps import require_admin, get_current_user

router = APIRouter(prefix="/admin/governance", tags=["Admin Governance"], dependencies=[Depends(require_admin)])


def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


# ----------------- 1. GOVERNANCE OVERVIEW -----------------

@router.get("/overview", response_model=GovernanceOverviewResponse)
def get_governance_overview(db: Session = Depends(get_db)) -> GovernanceOverviewResponse:
    """Institutional mentor governance overview KPIs and priority attention queue."""
    now = datetime.now(timezone.utc)
    naive_now = now.replace(tzinfo=None)

    total_mentors = db.query(Mentor).count()
    assigned_students = db.query(Student).filter(Student.mentor_id.isnot(None)).count()

    # Active mentoring support: students with pending/in-progress tasks or a meeting in last 30 days
    thirty_days_ago = naive_now - timedelta(days=30)
    students_with_tasks = set(
        r[0] for r in db.query(StudentTask.student_id).filter(StudentTask.status != "completed").all()
    )
    students_with_recent_meeting = set(
        r[0] for r in db.query(MentorMeeting.student_id).filter(MentorMeeting.meeting_date >= thirty_days_ago).all()
    )
    active_support_count = len(students_with_tasks.union(students_with_recent_meeting))

    # Awaiting follow-up: students with a meeting scheduled or follow-up date pending
    meetings_with_followup = db.query(MentorMeeting).filter(MentorMeeting.next_followup_date.isnot(None)).all()
    awaiting_followup_students = set(m.student_id for m in meetings_with_followup if m.meeting_status != "cancelled")
    
    # Overdue follow-ups
    overdue_followups = [
        m for m in meetings_with_followup
        if m.meeting_status != "cancelled" and _to_utc(m.next_followup_date) < now
    ]
    overdue_followups_count = len(overdue_followups)

    # Pending intervention decisions
    pending_decisions = db.query(Intervention).filter_by(status="proposed").count()

    # Attention Queue generation (actionable cases)
    attention_queue: List[AttentionQueueItem] = []
    case_idx = 1

    # A. Overdue follow-ups
    for m in overdue_followups[:5]:
        st = m.student
        men = m.mentor
        diff_days = (now.date() - _to_utc(m.next_followup_date).date()).days
        attention_queue.append(
            AttentionQueueItem(
                case_id=f"CASE-{case_idx:03d}",
                student_id=st.id,
                student_name=st.user.full_name if st.user else "Student",
                registration_number=st.registration_number,
                section=st.section,
                mentor_id=men.id,
                mentor_name=men.user.full_name if men.user else "Mentor",
                issue_type="Overdue Follow-up",
                severity="high" if diff_days > 7 else "medium",
                detail=f"Follow-up was scheduled for {m.next_followup_date.strftime('%b %d')} ({diff_days} days overdue).",
                action_label="Review Meeting Record",
            )
        )
        case_idx += 1

    # B. Overdue academic tasks
    overdue_tasks = (
        db.query(StudentTask)
        .filter(StudentTask.status != "completed", StudentTask.due_date < naive_now)
        .order_by(StudentTask.due_date.asc())
        .limit(5)
        .all()
    )
    for t in overdue_tasks:
        st = t.student
        men = st.mentor if st else None
        due_utc = _to_utc(t.due_date)
        diff_days = (now.date() - due_utc.date()).days if due_utc else 0
        attention_queue.append(
            AttentionQueueItem(
                case_id=f"CASE-{case_idx:03d}",
                student_id=st.id if st else 0,
                student_name=st.user.full_name if (st and st.user) else "Student",
                registration_number=st.registration_number if st else "",
                section=st.section if st else "",
                mentor_id=men.id if men else 0,
                mentor_name=men.user.full_name if (men and men.user) else "Unassigned",
                issue_type="Overdue Task",
                severity="high" if diff_days > 5 else "medium",
                detail=f"Task '{t.title[:38]}' is {diff_days}d past deadline ({t.course_code or 'General'}).",
                action_label="Inspect Task",
            )
        )
        case_idx += 1

    # C. Declining Trajectories (computed via OLS slope over W1-W6)
    students = db.query(Student).all()
    for s in students:
        metrics = (
            db.query(WeeklyAcademicMetric)
            .filter(WeeklyAcademicMetric.student_id == s.id, WeeklyAcademicMetric.week_number <= 6)
            .order_by(WeeklyAcademicMetric.week_number.asc())
            .all()
        )
        if len(metrics) >= 3:
            xs = [m.week_number for m in metrics]
            ys = [m.assessment_score for m in metrics]
            x_bar = sum(xs) / len(xs)
            y_bar = sum(ys) / len(ys)
            denom = sum((x - x_bar) ** 2 for x in xs)
            numer = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys))
            slope = numer / denom if denom > 0 else 0.0
            if slope < -1.0:
                men = s.mentor
                attention_queue.append(
                    AttentionQueueItem(
                        case_id=f"CASE-{case_idx:03d}",
                        student_id=s.id,
                        student_name=s.user.full_name if s.user else "Student",
                        registration_number=s.registration_number,
                        section=s.section,
                        mentor_id=men.id if men else 0,
                        mentor_name=men.user.full_name if (men and men.user) else "Unassigned",
                        issue_type="Declining Trajectory",
                        severity="high",
                        detail=f"Continuous score velocity declining (slope {slope:.2f}/wk) across W1–W6.",
                        action_label="Review Trajectory",
                    )
                )
                case_idx += 1
                if case_idx > 10:
                    break

    # D. Pending Intervention Decisions
    pending_invs = db.query(Intervention).filter_by(status="proposed").limit(4).all()
    for inv in pending_invs:
        st = inv.student
        men = inv.mentor
        attention_queue.append(
            AttentionQueueItem(
                case_id=f"CASE-{case_idx:03d}",
                student_id=st.id if st else 0,
                student_name=st.user.full_name if (st and st.user) else "Student",
                registration_number=st.registration_number if st else "",
                section=st.section if st else "",
                mentor_id=men.id if men else 0,
                mentor_name=men.user.full_name if (men and men.user) else "Unassigned",
                issue_type="Pending Decision",
                severity="medium" if inv.priority != "High" else "high",
                detail=f"Recommendation for {inv.intervention_type} awaits mentor review.",
                action_label="View Intervention",
            )
        )
        case_idx += 1

    return GovernanceOverviewResponse(
        total_active_mentors=total_mentors,
        total_assigned_students=assigned_students,
        students_with_active_support=active_support_count,
        students_awaiting_followup=len(awaiting_followup_students),
        pending_intervention_decisions=pending_decisions,
        overdue_followups_count=overdue_followups_count,
        attention_queue=attention_queue[:12],
    )


# ----------------- 2. MENTOR WORKLOAD & ALLOCATION -----------------

@router.get("/mentor-workload", response_model=List[MentorWorkloadItem])
def get_mentor_workload(db: Session = Depends(get_db)) -> List[MentorWorkloadItem]:
    """Mentor allocation quotas, remaining capacity, and load percentages."""
    mentors = db.query(Mentor).all()
    result = []
    for m in mentors:
        assigned = len(m.students)
        quota = m.workload_cap or 10
        rem = max(0, quota - assigned)
        pct = round(100.0 * assigned / quota, 1) if quota > 0 else 100.0
        result.append(
            MentorWorkloadItem(
                mentor_id=m.id,
                faculty_code=m.faculty_code,
                mentor_name=m.user.full_name if m.user else "Faculty Mentor",
                department=m.department,
                assigned_students=assigned,
                max_quota=quota,
                remaining_capacity=rem,
                allocated_percentage=pct,
            )
        )
    return result


# ----------------- 3. STUDENT SUPPORT DISTRIBUTION -----------------

@router.get("/student-distribution", response_model=List[StudentDistributionItem])
def get_student_distribution(db: Session = Depends(get_db)) -> List[StudentDistributionItem]:
    """Breakdown of On Track, Watch, and Needs Review students by faculty mentor."""
    mentors = db.query(Mentor).all()
    result = []
    for m in mentors:
        stus = m.students
        tot = len(stus)
        on_track = sum(1 for s in stus if s.academic_status == "ON TRACK")
        watch = sum(1 for s in stus if s.academic_status == "WATCH")
        review = sum(1 for s in stus if s.academic_status == "NEEDS REVIEW")

        result.append(
            StudentDistributionItem(
                mentor_id=m.id,
                faculty_code=m.faculty_code,
                mentor_name=m.user.full_name if m.user else "Faculty Mentor",
                total_students=tot,
                on_track_count=on_track,
                on_track_pct=round(100.0 * on_track / tot, 1) if tot > 0 else 0.0,
                watch_count=watch,
                watch_pct=round(100.0 * watch / tot, 1) if tot > 0 else 0.0,
                needs_review_count=review,
                needs_review_pct=round(100.0 * review / tot, 1) if tot > 0 else 0.0,
            )
        )
    return result


# ----------------- 4. MENTOR PERFORMANCE DIRECTORY & PROFILES -----------------

@router.get("/mentors", response_model=List[MentorDirectoryItem])
def get_mentor_directory(
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[MentorDirectoryItem]:
    """Searchable faculty mentor directory with academic support and engagement metrics."""
    q = db.query(Mentor).join(User)
    if search:
        s_term = f"%{search.strip()}%"
        q = q.filter((Mentor.faculty_code.ilike(s_term)) | (User.full_name.ilike(s_term)))
    if department:
        q = q.filter(Mentor.department == department.strip())

    mentors = q.order_by(Mentor.faculty_code.asc()).all()
    naive_now = datetime.now(timezone.utc).replace(tzinfo=None)

    items = []
    for m in mentors:
        stus = m.students
        tot = len(stus)
        cap = m.workload_cap or 10
        on_track = sum(1 for s in stus if s.academic_status == "ON TRACK")
        watch = sum(1 for s in stus if s.academic_status == "WATCH")
        review = sum(1 for s in stus if s.academic_status == "NEEDS REVIEW")

        mentee_ids = [s.id for s in stus]
        tasks = db.query(StudentTask).filter(StudentTask.student_id.in_(mentee_ids)).all() if mentee_ids else []
        pending_t = sum(1 for t in tasks if t.status == "pending")
        completed_t = sum(1 for t in tasks if t.status == "completed")
        overdue_t = sum(1 for t in tasks if t.status != "completed" and t.due_date and t.due_date < naive_now)

        meetings_count = db.query(MentorMeeting).filter_by(mentor_id=m.id).count()
        pending_invs = db.query(Intervention).filter_by(mentor_id=m.id, status="proposed").count()

        items.append(
            MentorDirectoryItem(
                mentor_id=m.id,
                faculty_code=m.faculty_code,
                name=m.user.full_name if m.user else "Faculty Mentor",
                department=m.department,
                designation=m.designation,
                assigned_students=tot,
                capacity_utilization_pct=round(100.0 * tot / cap, 1) if cap > 0 else 100.0,
                on_track_count=on_track,
                watch_count=watch,
                needs_review_count=review,
                pending_tasks=pending_t,
                completed_tasks=completed_t,
                overdue_tasks=overdue_t,
                total_meetings=meetings_count,
                pending_intervention_approvals=pending_invs,
            )
        )
    return items


@router.get("/mentors/{mentor_id}", response_model=MentorGovernanceProfileResponse)
def get_mentor_governance_profile(
    mentor_id: int,
    db: Session = Depends(get_db),
) -> MentorGovernanceProfileResponse:
    """Consolidated 4-group governance profile for an individual faculty mentor."""
    mentor = db.query(Mentor).filter_by(id=mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found.")

    stus = mentor.students
    tot = len(stus)
    mentee_ids = [s.id for s in stus]
    naive_now = datetime.now(timezone.utc).replace(tzinfo=None)
    now = datetime.now(timezone.utc)

    # Group 1: Assigned cohort
    on_track = sum(1 for s in stus if s.academic_status == "ON TRACK")
    watch = sum(1 for s in stus if s.academic_status == "WATCH")
    review = sum(1 for s in stus if s.academic_status == "NEEDS REVIEW")

    # Averages
    all_perfs = (
        db.query(StudentSubjectPerformance).filter(StudentSubjectPerformance.student_id.in_(mentee_ids)).all()
        if mentee_ids else []
    )
    if all_perfs:
        avg_att = round(sum(p.attendance_percentage for p in all_perfs) / len(all_perfs), 1)
        avg_ass = round(sum(p.internal_marks for p in all_perfs) / (len(all_perfs) * 30.0) * 100.0, 1)
    else:
        avg_att, avg_ass = 80.0, 75.0

    attention_needed = sum(1 for s in stus if s.academic_status in ("WATCH", "NEEDS REVIEW"))

    # Group 2: Academic support activity
    tasks = db.query(StudentTask).filter(StudentTask.student_id.in_(mentee_ids)).all() if mentee_ids else []
    t_assigned = len(tasks)
    t_completed = sum(1 for t in tasks if t.status == "completed")
    t_in_progress = sum(1 for t in tasks if t.status == "pending")
    t_overdue = sum(1 for t in tasks if t.status != "completed" and t.due_date and t.due_date < naive_now)

    students_with_uncompleted = len(set(t.student_id for t in tasks if t.status != "completed"))

    # Group 3: Mentoring engagement
    meetings = db.query(MentorMeeting).filter_by(mentor_id=mentor.id).all()
    m_total = len(meetings)
    met_students = set(m.student_id for m in meetings)
    unique_met = len(met_students)
    students_no_meeting = tot - unique_met

    followups_sched = sum(1 for m in meetings if m.next_followup_date is not None and m.meeting_status != "cancelled")
    followups_over = sum(
        1 for m in meetings
        if m.next_followup_date and _to_utc(m.next_followup_date) < now and m.meeting_status != "cancelled"
    )

    weekly_freq: Dict[str, int] = {}
    for i in range(1, 9):
        weekly_freq[f"W{i}"] = 0
    # Group meetings by roughly week if within semester dates
    for m in meetings:
        wk = 1 + (m.meeting_date.date() - datetime(2026, 8, 3).date()).days // 7
        if 1 <= wk <= 8:
            weekly_freq[f"W{wk}"] = weekly_freq.get(f"W{wk}", 0) + 1

    # Group 4: Intervention management
    invs = db.query(Intervention).filter_by(mentor_id=mentor.id).all()
    i_awaiting = sum(1 for i in invs if i.status == "proposed")
    i_approved = sum(1 for i in invs if i.status in ("approved", "in_progress"))
    i_dismissed = sum(1 for i in invs if i.status == "rejected")
    i_completed = sum(1 for i in invs if i.status == "completed")

    return MentorGovernanceProfileResponse(
        mentor_id=mentor.id,
        faculty_code=mentor.faculty_code,
        name=mentor.user.full_name if mentor.user else "Faculty Mentor",
        department=mentor.department,
        designation=mentor.designation,
        workload_cap=mentor.workload_cap,
        total_assigned_students=tot,
        cohort_status_distribution={"on_track": on_track, "watch": watch, "needs_review": review},
        avg_attendance_pct=avg_att,
        avg_assessment_pct=avg_ass,
        students_requiring_attention=attention_needed,
        tasks_assigned=t_assigned,
        tasks_completed=t_completed,
        tasks_in_progress=t_in_progress,
        tasks_overdue=t_overdue,
        students_with_uncompleted_tasks=students_with_uncompleted,
        total_meetings=m_total,
        unique_students_met=unique_met,
        students_without_meeting=students_no_meeting,
        followups_scheduled=followups_sched,
        followups_overdue=followups_over,
        meeting_frequency_weekly=weekly_freq,
        recommendations_awaiting_approval=i_awaiting,
        approved_interventions=i_approved,
        dismissed_recommendations=i_dismissed,
        completed_interventions=i_completed,
    )


# ----------------- 5. STUDENT-MENTOR RELATIONSHIPS -----------------

@router.get("/relationships", response_model=StudentMentorRelationshipResponse)
def get_student_mentor_relationships(
    search: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    mentor_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
) -> StudentMentorRelationshipResponse:
    """Searchable student-mentor relationships matrix with live status, attendance, and tasks."""
    q = db.query(Student).join(User)

    if search:
        s_term = f"%{search.strip()}%"
        q = q.filter((Student.registration_number.ilike(s_term)) | (User.full_name.ilike(s_term)))
    if section:
        q = q.filter(Student.section == section.strip())
    if mentor_id:
        q = q.filter(Student.mentor_id == mentor_id)
    if status_filter:
        q = q.filter(Student.academic_status == status_filter.strip().upper())

    total = q.count()
    students = q.order_by(Student.registration_number.asc()).offset((page - 1) * page_size).limit(page_size).all()

    now = datetime.now(timezone.utc)
    naive_now = now.replace(tzinfo=None)

    items: List[StudentMentorRelationshipItem] = []
    for s in students:
        perfs = db.query(StudentSubjectPerformance).filter_by(student_id=s.id).all()
        deliv = sum(p.delivered for p in perfs) or 1
        att = sum(p.attended + p.duty_leave for p in perfs)
        att_pct = min(100.0, round(100.0 * att / deliv, 1))
        marks_pct = round(
            sum(p.internal_marks for p in perfs) / (len(perfs) * 30.0) * 100.0, 1
        ) if perfs else 75.0

        tasks = db.query(StudentTask).filter_by(student_id=s.id).all()
        active_t = sum(1 for t in tasks if t.status != "completed")
        completed_t = sum(1 for t in tasks if t.status == "completed")
        has_overdue_task = any(t.status != "completed" and t.due_date and t.due_date < naive_now for t in tasks)

        # Last meeting & next follow-up
        meetings = db.query(MentorMeeting).filter_by(student_id=s.id).order_by(MentorMeeting.meeting_date.desc()).all()
        last_m = meetings[0] if meetings else None
        
        # Next follow-up is closest future (or pending) follow-up date
        upcoming_meetings = [m for m in meetings if m.next_followup_date is not None and m.meeting_status != "cancelled"]
        next_followup_date = upcoming_meetings[0].next_followup_date if upcoming_meetings else None

        has_overdue_followup = bool(
            next_followup_date and _to_utc(next_followup_date) < now
        )

        # Support status classification
        if has_overdue_task or has_overdue_followup or s.academic_status == "NEEDS REVIEW":
            support_status = "Attention Required"
        elif active_t > 0:
            support_status = "Active Recovery"
        elif len(meetings) > 0:
            support_status = "Active Mentoring"
        else:
            support_status = "Standard Tracking"

        men = s.mentor
        items.append(
            StudentMentorRelationshipItem(
                student_id=s.id,
                student_name=s.user.full_name if s.user else "Student",
                registration_number=s.registration_number,
                section=s.section,
                mentor_id=men.id if men else None,
                mentor_name=men.user.full_name if (men and men.user) else None,
                faculty_code=men.faculty_code if men else None,
                academic_status=s.academic_status,
                attendance_pct=att_pct,
                assessment_pct=marks_pct,
                active_tasks_count=active_t,
                completed_tasks_count=completed_t,
                last_meeting_date=last_m.meeting_date if last_m else None,
                next_followup_date=next_followup_date,
                support_status=support_status,
            )
        )

    return StudentMentorRelationshipResponse(
        total=total,
        page=page,
        page_size=page_size,
        relationships=items,
    )


@router.get("/students/{student_id}/governance", response_model=StudentGovernanceDetailResponse)
def get_student_governance_detail(
    student_id: int,
    db: Session = Depends(get_db),
) -> StudentGovernanceDetailResponse:
    """Deep governance profile for an individual student (slide-over drawer)."""
    s = db.query(Student).filter_by(id=student_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    perfs = db.query(StudentSubjectPerformance).filter_by(student_id=s.id).all()
    deliv = sum(p.delivered for p in perfs) or 1
    att = sum(p.attended + p.duty_leave for p in perfs)
    att_pct = min(100.0, round(100.0 * att / deliv, 1))
    marks_pct = round(
        sum(p.internal_marks for p in perfs) / (len(perfs) * 30.0) * 100.0, 1
    ) if perfs else 75.0

    # Weak subjects (marks < 75% or attendance < 75%)
    weak_subjects = []
    for p in perfs:
        s_marks_pct = round((p.internal_marks / 30.0) * 100.0, 1)
        if s_marks_pct < 75.0 or p.attendance_percentage < 75.0:
            weak_subjects.append({
                "subject_code": p.subject.subject_code if p.subject else "",
                "subject_name": p.subject.subject_name if p.subject else "",
                "marks_pct": s_marks_pct,
                "attendance_pct": round(p.attendance_percentage, 1),
            })

    # Observed and projected trajectory
    weekly = (
        db.query(WeeklyAcademicMetric)
        .filter_by(student_id=s.id)
        .order_by(WeeklyAcademicMetric.week_number.asc())
        .all()
    )
    observed = []
    projected = []
    for w in weekly:
        point = {
            "week_number": w.week_number,
            "assessment_score": round(w.assessment_score, 1),
            "attendance_pct": round(w.attendance_percentage, 1),
        }
        if w.week_number > 6:
            projected.append(point)
        else:
            observed.append(point)

    # Meetings
    meetings_data = []
    meetings = db.query(MentorMeeting).filter_by(student_id=s.id).order_by(MentorMeeting.meeting_date.desc()).all()
    upcoming_followup = None
    for m in meetings:
        meetings_data.append({
            "id": m.id,
            "meeting_date": m.meeting_date.isoformat(),
            "meeting_type": m.meeting_type,
            "duration_minutes": m.duration_minutes,
            "discussion_summary": m.discussion_summary,
            "academic_concerns": m.academic_concerns,
            "agreed_actions": m.agreed_actions,
            "next_followup_date": m.next_followup_date.isoformat() if m.next_followup_date else None,
            "meeting_status": m.meeting_status,
        })
        if m.next_followup_date and upcoming_followup is None and m.meeting_status != "cancelled":
            upcoming_followup = m.next_followup_date

    # Tasks
    tasks_data = []
    tasks = db.query(StudentTask).filter_by(student_id=s.id).order_by(StudentTask.created_at.desc()).all()
    for t in tasks:
        tasks_data.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "course_code": t.course_code,
            "priority": t.priority,
            "status": t.status,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "source": t.source,
        })

    # Interventions & decisions
    invs_data = []
    decisions_data = []
    invs = db.query(Intervention).filter_by(student_id=s.id).all()
    for i in invs:
        invs_data.append({
            "id": i.id,
            "intervention_type": i.intervention_type,
            "recommendation": i.recommendation,
            "reason": i.reason,
            "priority": i.priority,
            "status": i.status,
            "created_at": i.created_at.isoformat(),
        })
        for d in i.decisions:
            decisions_data.append({
                "decision_id": d.id,
                "intervention_id": d.intervention_id,
                "decision": d.decision,
                "comments": d.comments,
                "decided_at": d.decided_at.isoformat(),
            })

    men = s.mentor
    return StudentGovernanceDetailResponse(
        student_id=s.id,
        name=s.user.full_name if s.user else "Student",
        registration_number=s.registration_number,
        section=s.section,
        department=s.department,
        academic_status=s.academic_status,
        cgpa=round(s.sem2_sgpa or 7.5, 2),
        attendance_pct=att_pct,
        internal_marks_pct=marks_pct,
        mentor_id=men.id if men else None,
        mentor_name=men.user.full_name if (men and men.user) else None,
        faculty_code=men.faculty_code if men else None,
        observed_trajectory=observed,
        projected_trajectory=projected,
        weak_subjects=weak_subjects,
        meetings=meetings_data,
        upcoming_followup=upcoming_followup,
        tasks=tasks_data,
        interventions=invs_data,
        decisions=decisions_data,
    )


# ----------------- 6. MEETING & FOLLOW-UP MONITORING -----------------

@router.get("/meetings/analytics", response_model=MeetingAnalyticsResponse)
def get_meeting_analytics(db: Session = Depends(get_db)) -> MeetingAnalyticsResponse:
    """Institutional analytics on mentoring session frequency, modalities, and follow-ups."""
    now = datetime.now(timezone.utc)
    meetings = db.query(MentorMeeting).all()
    total = len(meetings)

    all_students_count = db.query(Student).count()
    met_students = set(m.student_id for m in meetings)
    unique_met = len(met_students)
    without_meeting = all_students_count - unique_met

    by_mentor: Dict[str, int] = {}
    mentors = db.query(Mentor).all()
    for men in mentors:
        m_name = men.user.full_name if men.user else men.faculty_code
        by_mentor[m_name] = 0
    for m in meetings:
        men = m.mentor
        if men:
            m_name = men.user.full_name if men.user else men.faculty_code
            by_mentor[m_name] = by_mentor.get(m_name, 0) + 1

    by_modality: Dict[str, int] = {"In Person": 0, "Online": 0, "Phone": 0}
    for m in meetings:
        mod = m.meeting_type or "In Person"
        by_modality[mod] = by_modality.get(mod, 0) + 1

    weekly: Dict[str, int] = {f"W{i}": 0 for i in range(1, 9)}
    for m in meetings:
        wk = 1 + (m.meeting_date.date() - datetime(2026, 8, 3).date()).days // 7
        if 1 <= wk <= 8:
            weekly[f"W{wk}"] = weekly.get(f"W{wk}", 0) + 1

    upcoming_count = sum(
        1 for m in meetings
        if m.next_followup_date and _to_utc(m.next_followup_date) >= now and m.meeting_status != "cancelled"
    )
    overdue_count = sum(
        1 for m in meetings
        if m.next_followup_date and _to_utc(m.next_followup_date) < now and m.meeting_status != "cancelled"
    )

    return MeetingAnalyticsResponse(
        total_meetings=total,
        unique_students_met=unique_met,
        students_without_recorded_meeting=without_meeting,
        meetings_by_mentor=by_mentor,
        meetings_by_modality=by_modality,
        weekly_frequency=weekly,
        upcoming_followups_count=upcoming_count,
        overdue_followups_count=overdue_count,
    )


@router.get("/meetings")
def get_admin_meetings_list(
    mentor_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    section: Optional[str] = Query(None),
    meeting_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Paginated list of all recorded mentoring meetings across the university."""
    q = db.query(MentorMeeting).join(Student)
    if mentor_id:
        q = q.filter(MentorMeeting.mentor_id == mentor_id)
    if student_id:
        q = q.filter(MentorMeeting.student_id == student_id)
    if section:
        q = q.filter(Student.section == section.strip())
    if meeting_type:
        q = q.filter(MentorMeeting.meeting_type == meeting_type.strip())

    total = q.count()
    meetings = q.order_by(MentorMeeting.meeting_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    now = datetime.now(timezone.utc)
    items = []
    for m in meetings:
        st = m.student
        men = m.mentor
        f_status = "None"
        if m.next_followup_date is not None:
            f_dt = _to_utc(m.next_followup_date)
            if m.meeting_status == "cancelled":
                f_status = "Cancelled"
            elif f_dt < now:
                f_status = "Overdue"
            else:
                f_status = "Upcoming"

        items.append({
            "id": m.id,
            "mentor_id": m.mentor_id,
            "mentor_name": men.user.full_name if (men and men.user) else "Mentor",
            "faculty_code": men.faculty_code if men else "",
            "student_id": m.student_id,
            "student_name": st.user.full_name if (st and st.user) else "Student",
            "registration_number": st.registration_number if st else "",
            "section": st.section if st else "",
            "meeting_date": m.meeting_date.isoformat(),
            "meeting_type": m.meeting_type,
            "duration_minutes": m.duration_minutes,
            "discussion_summary": m.discussion_summary,
            "academic_concerns": m.academic_concerns,
            "agreed_actions": m.agreed_actions,
            "next_followup_date": m.next_followup_date.isoformat() if m.next_followup_date else None,
            "meeting_status": m.meeting_status,
            "followup_status": f_status,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "meetings": items,
    }


@router.get("/followups", response_model=List[FollowupQueueItem])
def get_followup_queue(db: Session = Depends(get_db)) -> List[FollowupQueueItem]:
    """Actionable queue of students awaiting mentoring follow-ups (both upcoming and overdue)."""
    now = datetime.now(timezone.utc)
    meetings = (
        db.query(MentorMeeting)
        .filter(MentorMeeting.next_followup_date.isnot(None), MentorMeeting.meeting_status != "cancelled")
        .order_by(MentorMeeting.next_followup_date.asc())
        .all()
    )

    items = []
    for m in meetings:
        f_dt = _to_utc(m.next_followup_date)
        diff = (f_dt.date() - now.date()).days
        st = m.student
        men = m.mentor
        items.append(
            FollowupQueueItem(
                meeting_id=m.id,
                student_id=m.student_id,
                student_name=st.user.full_name if (st and st.user) else "Student",
                registration_number=st.registration_number if st else "",
                section=st.section if st else "",
                mentor_id=m.mentor_id,
                mentor_name=men.user.full_name if (men and men.user) else "Mentor",
                meeting_date=m.meeting_date,
                next_followup_date=m.next_followup_date,
                days_difference=diff,
                status="Overdue" if diff < 0 else "Upcoming",
                agreed_actions=m.agreed_actions,
            )
        )
    return items


# ----------------- 7. INTERVENTION OVERSIGHT & ACTIONS -----------------

@router.get("/interventions", response_model=List[AdminInterventionItem])
def get_admin_interventions(
    status_filter: Optional[str] = Query(None),
    mentor_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[AdminInterventionItem]:
    """Institution-wide intervention oversight feed with supporting evidence and decision history."""
    q = db.query(Intervention)
    if status_filter:
        q = q.filter(Intervention.status == status_filter.strip())
    if mentor_id:
        q = q.filter(Intervention.mentor_id == mentor_id)
    if priority:
        q = q.filter(Intervention.priority == priority.strip())

    invs = q.order_by(Intervention.created_at.desc()).all()
    items = []
    for inv in invs:
        st = inv.student
        men = inv.mentor
        tasks = (
            db.query(StudentTask)
            .filter_by(student_id=inv.student_id, playbook_id=inv.playbook_id)
            .all()
        )
        task_data = [
            {"id": t.id, "title": t.title, "status": t.status, "due_date": t.due_date.isoformat() if t.due_date else None}
            for t in tasks
        ]

        items.append(
            AdminInterventionItem(
                id=inv.id,
                student_id=inv.student_id,
                student_name=st.user.full_name if (st and st.user) else "Student",
                registration_number=st.registration_number if st else "",
                section=st.section if st else "",
                mentor_id=inv.mentor_id,
                mentor_name=men.user.full_name if (men and men.user) else "Mentor",
                intervention_type=inv.intervention_type,
                course_code=inv.playbook_id,
                priority=inv.priority,
                status=inv.status,
                recommendation=inv.recommendation,
                reason=inv.reason,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                associated_tasks=task_data,
                decisions_count=len(inv.decisions),
                admin_reviewed=False,
                admin_notes=None,
            )
        )
    return items


@router.post("/interventions/{intervention_id}/review")
def review_intervention_admin(
    intervention_id: int,
    payload: AdminInterventionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Administrative oversight action on an intervention (e.g. flag for review or record note).
    Preserves academic autonomy by auditing administrative governance actions.
    """
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    audit = AuditLog(
        user_id=current_user.id,
        actor_role="admin",
        action=f"admin_intervention_{payload.action}",
        entity_type="intervention",
        entity_id=str(inv.id),
        details=f"Admin {current_user.full_name} applied '{payload.action}' on Intervention {inv.id} (Student {inv.student_id}, Mentor {inv.mentor_id}). Note: {payload.note}",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "action": payload.action,
        "intervention_id": inv.id,
        "message": f"Administrative action '{payload.action}' recorded in institutional audit log.",
    }
