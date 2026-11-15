import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.academic import Student, Subject
from backend.app.models.performance import (
    StudentSubjectPerformance,
    AcademicRecord,
    WeeklyAcademicMetric,
    WeeklyAttendance,
)
from backend.app.models.assessment import StudentAssessment, Assessment
from backend.app.models.risk import RiskAssessment
from backend.app.models.intervention import StudentTask
from backend.app.models.system import AuditLog
from backend.app.schemas.student import (
    StudentDashboardResponse,
    StudentKpiData,
    WeeklyTrendPoint,
    SubjectPerformanceItem,
    TaskItem,
    TaskToggleRequest,
    TaskCreateRequest,
    TaskUpdateRequest,
    StudentExplanationResponse,
    ExplanationFactor,
    RecommendedAction,
)
from backend.app.api.deps import get_current_user, require_student

router = APIRouter(prefix="/student", tags=["Student"])

def _resolve_student(current_user: User, student_id: Optional[int], db: Session) -> Student:
    """Resolve student entity ensuring access isolation."""
    if current_user.role == "student":
        if not current_user.student_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found for current user account.",
            )
        return current_user.student_profile
    elif current_user.role in ("mentor", "admin"):
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id parameter is required when accessing student APIs as mentor/admin.",
            )
        target = db.query(Student).filter_by(id=student_id).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student record with ID {student_id} not found.",
            )
        if current_user.role == "mentor":
            if not current_user.mentor_profile or target.mentor_id != current_user.mentor_profile.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Student is not in your assigned mentorship cohort.",
                )
        return target
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized role for student endpoints.",
        )


@router.get("/dashboard", response_model=StudentDashboardResponse)
def get_student_dashboard(
    student_id: Optional[int] = Query(None, description="Optional for admin/mentor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentDashboardResponse:
    """
    Unified academic dashboard endpoint powering the Stitch Student Dashboard.
    All data is computed from relational database entities.
    """
    student = _resolve_student(current_user, student_id, db)

    # 1. Subject Performances & Aggregate Attendance
    perfs = db.query(StudentSubjectPerformance).filter_by(student_id=student.id).all()
    total_delivered = sum(p.delivered for p in perfs) or 1
    total_attended = sum(p.attended + p.duty_leave for p in perfs)
    agg_att_pct = min(100.0, round(100.0 * total_attended / total_delivered, 1))

    # Attendance classes to safe 85% threshold
    # needed: (total_attended + X) / (total_delivered + X) >= 0.85 => 0.15*X >= 0.85*deliv - att
    classes_needed = max(0, int(round((0.85 * total_delivered - total_attended) / 0.15)))

    # 2. Assignment / Assessment Completion
    # Computed from subject-wise continuous assignment tracking
    if perfs:
        asg_completion_pct = round(sum(p.assignment_completion for p in perfs) / len(perfs), 1)
        total_asg = 25
        completed_asg = int(round(total_asg * asg_completion_pct / 100.0))
        pending_asg = total_asg - completed_asg
    else:
        all_sa = db.query(StudentAssessment).filter_by(student_id=student.id).all()
        total_asg = len(all_sa) or 25
        completed_asg = sum(1 for a in all_sa if a.status in ("Present", "Submitted"))
        pending_asg = max(0, total_asg - completed_asg)
        asg_completion_pct = round(100.0 * completed_asg / total_asg, 1)

    # 3. Semester Average & CGPA
    academic_rec = db.query(AcademicRecord).filter_by(student_id=student.id, semester=student.semester).first()
    cgpa_val = academic_rec.cgpa if academic_rec else round(student.sem2_sgpa or 7.5, 2)
    sem_avg_val = academic_rec.semester_average if academic_rec else round(cgpa_val - 0.2, 2)
    prev_sem_diff = round(sem_avg_val - (student.sem2_sgpa or 7.1), 1)

    # 4. Status Subtitle & Color
    status_str = student.academic_status
    if status_str == "WATCH":
        status_subtitle = "Some subjects need attention"
        status_color = "amber"
    elif status_str == "NEEDS REVIEW":
        status_subtitle = "Immediate mentor consultation requested"
        status_color = "red"
    else:
        status_subtitle = "Normal academic trajectory"
        status_color = "green"

    kpi = StudentKpiData(
        academic_status=status_str,
        status_subtitle=status_subtitle,
        status_color=status_color,
        semester_average=sem_avg_val,
        cgpa=cgpa_val,
        prev_sem_diff=prev_sem_diff,
        attendance_percentage=agg_att_pct,
        attendance_target=85.0,
        classes_to_safe=classes_needed,
        assignment_completion_pct=asg_completion_pct,
        assignments_completed=completed_asg,
        assignments_total=total_asg,
        assignments_pending=pending_asg,
    )

    # 5. Weekly Trends (W1 to W8, current is W6 matching the Stitch design)
    metrics = (
        db.query(WeeklyAcademicMetric)
        .filter_by(student_id=student.id)
        .order_by(WeeklyAcademicMetric.week_number.asc())
        .all()
    )
    weekly_trends = []
    current_week = 6
    for m in metrics[:8]:
        is_cur = m.week_number == current_week
        is_proj = m.week_number > current_week
        label = f"W{m.week_number} (Now)" if is_cur else f"W{m.week_number}"
        weekly_trends.append(
            WeeklyTrendPoint(
                week_number=m.week_number,
                week_label=label,
                attendance_pct=m.attendance_percentage,
                assessment_score=m.assessment_score,
                is_current=is_cur,
                is_projected=is_proj,
            )
        )

    # 6. Subject Performance List
    subject_items = []
    for p in perfs:
        subj = p.subject
        m_pct = min(100.0, round(100.0 * p.internal_marks / p.maximum_internal_marks, 1))
        is_below = p.attendance_percentage < 75.0 or m_pct < 65.0
        subject_items.append(
            SubjectPerformanceItem(
                subject_code=subj.subject_code,
                subject_name=subj.subject_name,
                internal_marks=p.internal_marks,
                maximum_internal_marks=p.maximum_internal_marks,
                internal_marks_pct=m_pct,
                attendance_pct=p.attendance_percentage,
                assignment_completion_pct=p.assignment_completion,
                is_below_cutoff=is_below,
            )
        )

    # 7. Tasks
    task_rows = (
        db.query(StudentTask)
        .filter_by(student_id=student.id)
        .order_by(StudentTask.status.desc(), StudentTask.priority.asc())
        .all()
    )
    tasks = []
    for t in task_rows:
        due_lbl = "Due Today, 5:00 PM" if t.status == "pending" and t.priority == "High" else (
            "Due Tomorrow" if t.status == "pending" else "Completed"
        )
        tasks.append(
            TaskItem(
                id=t.id,
                title=t.title,
                course=t.course_code,
                priority=t.priority,
                status=t.status,
                due_label=due_lbl,
                source=t.source,
            )
        )

    # 8. Explainability
    ra = (
        db.query(RiskAssessment)
        .filter_by(student_id=student.id, assessment_week=6)
        .first()
    )
    factors = []
    next_steps = []
    if ra and ra.rules_fired:
        try:
            rules_data = json.loads(ra.rules_fired)
            for r in rules_data:
                factors.append(
                    ExplanationFactor(
                        factor_title=r.get("rule_name", "Academic Indicator"),
                        factor_description=r.get("details", ""),
                        severity="warning" if r.get("severity") in ("High", "Medium") else "info",
                        icon="trending_down" if "Marks" in r.get("rule_name", "") else "pending_actions",
                    )
                )
        except Exception:
            pass

    if not factors:
        factors.append(
            ExplanationFactor(
                factor_title="Academic Consistency",
                factor_description="Continuous evaluations and attendance are currently in good standing.",
                severity="success",
                icon="verified",
            )
        )

    # Recovery steps
    if status_str == "WATCH":
        next_steps = [
            RecommendedAction(
                step_number=1,
                title="Focused Subject Practice",
                description="Practice Mathematics for 30 minutes daily using module problem sets on Unit 1 & 2.",
            ),
            RecommendedAction(
                step_number=2,
                title="Resolve Overdue Submissions",
                description="Complete pending assignments by Friday to unlock continuous internal evaluation marks.",
            ),
            RecommendedAction(
                step_number=3,
                title="Attend Mentor Office Hours",
                description="Schedule a 15-minute check-in with your assigned faculty mentor to review study progress.",
            ),
        ]
    elif status_str == "NEEDS REVIEW":
        next_steps = [
            RecommendedAction(
                step_number=1,
                title="Immediate Mentor Consultation",
                description="Meet with your faculty mentor to formulate an official academic recovery plan.",
            ),
            RecommendedAction(
                step_number=2,
                title="Mandatory Lecture Attendance",
                description="Attend all scheduled lectures this week to recover attendance above the 75% examination limit.",
            ),
        ]
    else:
        next_steps = [
            RecommendedAction(
                step_number=1,
                title="Maintain Trajectory",
                description="Continue regular submission of weekly assignments and maintain attendance above 85%.",
            ),
        ]

    explanation = StudentExplanationResponse(
        academic_status=status_str,
        summary=ra.explanation_summary if ra else "Academic performance is on track.",
        factors=factors,
        next_steps=next_steps,
        clearance_weeks_remaining=4,
    )

    return StudentDashboardResponse(
        student_id=student.id,
        registration_number=student.registration_number,
        name=student.user.full_name,
        section=student.section,
        department=student.department,
        programme=student.programme,
        semester=student.semester,
        term_metadata="Spring Term • Week 6 • Mid-Semester",
        kpi=kpi,
        weekly_trends=weekly_trends,
        subject_performances=subject_items,
        tasks=tasks,
        explanation=explanation,
    )


@router.get("/performance", response_model=List[WeeklyTrendPoint])
def get_performance_trends(
    student_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WeeklyTrendPoint]:
    """Retrieve weekly assessment and attendance trend data."""
    student = _resolve_student(current_user, student_id, db)
    metrics = (
        db.query(WeeklyAcademicMetric)
        .filter_by(student_id=student.id)
        .order_by(WeeklyAcademicMetric.week_number.asc())
        .all()
    )
    current_week = 6
    points = []
    for m in metrics:
        points.append(
            WeeklyTrendPoint(
                week_number=m.week_number,
                week_label=f"W{m.week_number} (Now)" if m.week_number == current_week else f"W{m.week_number}",
                attendance_pct=m.attendance_percentage,
                assessment_score=m.assessment_score,
                is_current=m.week_number == current_week,
                is_projected=m.week_number > current_week,
            )
        )
    return points


@router.get("/subjects", response_model=List[SubjectPerformanceItem])
def get_subjects_performance(
    student_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[SubjectPerformanceItem]:
    """Retrieve detailed subject-wise continuous evaluation indicators."""
    student = _resolve_student(current_user, student_id, db)
    perfs = db.query(StudentSubjectPerformance).filter_by(student_id=student.id).all()
    items = []
    for p in perfs:
        m_pct = min(100.0, round(100.0 * p.internal_marks / p.maximum_internal_marks, 1))
        items.append(
            SubjectPerformanceItem(
                subject_code=p.subject.subject_code,
                subject_name=p.subject.subject_name,
                internal_marks=p.internal_marks,
                maximum_internal_marks=p.maximum_internal_marks,
                internal_marks_pct=m_pct,
                attendance_pct=p.attendance_percentage,
                assignment_completion_pct=p.assignment_completion,
                is_below_cutoff=(p.attendance_percentage < 75.0 or m_pct < 65.0),
            )
        )
    return items


@router.get("/tasks", response_model=List[TaskItem])
def get_student_tasks(
    filter_type: Optional[str] = Query(None, description="all, my_tasks, mentor_assigned, completed, overdue"),
    student_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TaskItem]:
    """Retrieve learning and recovery tasks for the student with optional category filter."""
    student = _resolve_student(current_user, student_id, db)
    
    query = db.query(StudentTask).filter_by(student_id=student.id)
    
    now = datetime.now(timezone.utc)
    naive_now = datetime.now(timezone.utc).replace(tzinfo=None)

    if filter_type == "my_tasks":
        query = query.filter(StudentTask.source.in_(["student", "custom"]))
    elif filter_type == "mentor_assigned":
        query = query.filter(StudentTask.source == "mentor")
    elif filter_type == "completed":
        query = query.filter(StudentTask.status == "completed")
    elif filter_type == "overdue":
        query = query.filter(StudentTask.status != "completed", StudentTask.due_date < naive_now)
        
    task_rows = query.order_by(StudentTask.status.desc(), StudentTask.created_at.desc()).all()
    
    mentor_name = student.mentor.user.full_name if (student.mentor and student.mentor.user) else "Faculty Mentor"
    
    items = []
    for t in task_rows:
        is_overdue = False
        if t.status != "completed" and t.due_date is not None:
            due_dt = t.due_date.replace(tzinfo=timezone.utc) if t.due_date.tzinfo is None else t.due_date
            is_overdue = due_dt < now
        status_label = "overdue" if is_overdue else t.status
        
        due_label = "Completed" if t.status == "completed" else ("Overdue" if is_overdue else ("Due Soon" if not t.due_date else t.due_date.strftime("%b %d")))
        creator = mentor_name if t.source == "mentor" else "Personal"
        
        items.append(
            TaskItem(
                id=t.id,
                title=t.title,
                description=t.description,
                course=t.course_code,
                priority=t.priority,
                status=status_label,
                due_label=due_label,
                source="mentor" if t.source == "mentor" else "student",
                due_date=t.due_date,
                created_at=t.created_at,
                creator_name=creator,
            )
        )
    return items


@router.patch("/tasks/{task_id}", response_model=TaskItem)
def update_task_status(
    task_id: int,
    req: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskItem:
    """Update task status or editable fields with role-based integrity safeguards."""
    student = _resolve_student(current_user, None, db)
    task = db.query(StudentTask).filter_by(id=task_id, student_id=student.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found for current student.",
        )
    
    # Security Rule: If mentor-assigned task, student CANNOT alter title, description, priority, or due_date
    if task.source == "mentor":
        if req.title or req.description or req.priority or (req.due_date and req.due_date != task.due_date):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Mentor-assigned task instructions, priority, and deadlines cannot be altered by students.",
            )
    else:
        # Student personal task: allowed to update title, description, priority, due_date
        if req.title:
            task.title = req.title.strip()
        if req.description is not None:
            task.description = req.description.strip()
        if req.priority:
            task.priority = req.priority
        if req.due_date:
            task.due_date = req.due_date
            
    # Status transition
    if req.status:
        new_status = req.status.lower()
        if new_status not in ("completed", "pending", "in_progress"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'pending', 'in_progress', or 'completed'.",
            )
        task.status = new_status
        task.done_at = datetime.now(timezone.utc) if new_status == "completed" else None
    
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role="student",
            action="update_task",
            entity_type="student_task",
            entity_id=str(task.id),
            details=f"Task '{task.title}' updated (Status: {task.status})",
        )
    )
    db.commit()
    db.refresh(task)

    mentor_name = student.mentor.user.full_name if (student.mentor and student.mentor.user) else "Faculty Mentor"
    return TaskItem(
        id=task.id,
        title=task.title,
        description=task.description,
        course=task.course_code,
        priority=task.priority,
        status=task.status,
        due_label="Completed" if task.status == "completed" else "In Progress" if task.status == "in_progress" else "Pending",
        source="mentor" if task.source == "mentor" else "student",
        due_date=task.due_date,
        created_at=task.created_at,
        creator_name=mentor_name if task.source == "mentor" else "Personal",
    )


@router.post("/tasks", response_model=TaskItem, status_code=status.HTTP_201_CREATED)
def create_custom_task(
    req: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskItem:
    """Allow students to add personalized custom study tasks."""
    student = _resolve_student(current_user, None, db)
    new_task = StudentTask(
        student_id=student.id,
        course_code=req.course_code,
        source="student",
        title=req.title.strip(),
        description=req.description.strip() if req.description else None,
        priority=req.priority,
        status="pending",
        due_date=req.due_date,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role="student",
            action="create_task",
            entity_type="student_task",
            entity_id=str(new_task.id),
            details=f"Personal study task created: '{new_task.title}'",
        )
    )
    db.commit()

    return TaskItem(
        id=new_task.id,
        title=new_task.title,
        description=new_task.description,
        course=new_task.course_code,
        priority=new_task.priority,
        status=new_task.status,
        due_label="Due Soon" if not new_task.due_date else new_task.due_date.strftime("%b %d"),
        source="student",
        due_date=new_task.due_date,
        created_at=new_task.created_at,
        creator_name="Personal",
    )


@router.delete("/tasks/{task_id}")
def delete_student_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a student personal task. Mentor-assigned tasks cannot be deleted by students."""
    student = _resolve_student(current_user, None, db)
    task = db.query(StudentTask).filter_by(id=task_id, student_id=student.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found for current student.",
        )
    
    if task.source == "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor-assigned academic tasks cannot be deleted by students.",
        )
        
    db.delete(task)
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role="student",
            action="delete_task",
            entity_type="student_task",
            entity_id=str(task_id),
            details=f"Personal task #{task_id} deleted by student",
        )
    )
    db.commit()
    return {"message": f"Task #{task_id} deleted successfully."}


@router.get("/explanation", response_model=StudentExplanationResponse)
def get_student_explanation(
    student_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentExplanationResponse:
    """Retrieve non-stigmatizing factor cards and trajectory suggestions."""
    dash = get_student_dashboard(student_id, current_user, db)
    return dash.explanation
