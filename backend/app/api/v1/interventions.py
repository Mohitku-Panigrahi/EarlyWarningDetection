from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.academic import Student, Mentor
from backend.app.models.intervention import Intervention, MentorDecision, StudentTask
from backend.app.models.system import AuditLog
from backend.app.schemas.intervention import (
    InterventionCreate,
    InterventionUpdate,
    InterventionActionRequest,
    InterventionResponse,
    MentorDecisionItem,
)
from backend.app.api.deps import get_current_user, require_mentor_or_admin

router = APIRouter(prefix="/interventions", tags=["Interventions"])

def _format_intervention_response(inv: Intervention) -> InterventionResponse:
    decisions_list = [
        MentorDecisionItem(
            id=d.id,
            decision=d.decision,
            comments=d.comments,
            decided_at=d.decided_at,
        )
        for d in inv.decisions
    ]
    return InterventionResponse(
        id=inv.id,
        student_id=inv.student_id,
        student_name=inv.student.user.full_name,
        registration_number=inv.student.registration_number,
        mentor_id=inv.mentor_id,
        mentor_name=inv.mentor.user.full_name,
        intervention_type=inv.intervention_type,
        recommendation=inv.recommendation,
        reason=inv.reason,
        priority=inv.priority,
        status=inv.status,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        decisions=decisions_list,
    )

@router.post("", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
def create_intervention(
    data: InterventionCreate,
    current_user: User = Depends(require_mentor_or_admin),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """Propose a new human-in-the-loop intervention recommendation."""
    student = db.query(Student).filter_by(id=data.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    mentor_id = student.mentor_id
    if current_user.role == "mentor":
        if not current_user.mentor_profile or student.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security violation: Student is not in your assigned cohort.",
            )
        mentor_id = current_user.mentor_profile.id

    inv = Intervention(
        student_id=student.id,
        mentor_id=mentor_id,
        playbook_id=data.playbook_id,
        intervention_type=data.intervention_type,
        recommendation=data.recommendation,
        reason=data.reason,
        priority=data.priority,
        status="proposed",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="propose_intervention",
            entity_type="intervention",
            entity_id=str(inv.id),
            details=f"Proposed '{inv.intervention_type}' for student {student.registration_number}",
        )
    )
    db.commit()
    return _format_intervention_response(inv)


@router.get("/{intervention_id}", response_model=InterventionResponse)
def get_intervention(
    intervention_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """Retrieve full details and decision audit trail of an intervention."""
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    # Isolation check
    if current_user.role == "student":
        if not current_user.student_profile or inv.student_id != current_user.student_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    elif current_user.role == "mentor":
        if not current_user.mentor_profile or inv.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return _format_intervention_response(inv)


@router.patch("/{intervention_id}", response_model=InterventionResponse)
def update_intervention(
    intervention_id: int,
    data: InterventionUpdate,
    current_user: User = Depends(require_mentor_or_admin),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """Edit or update an intervention recommendation."""
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    if current_user.role == "mentor":
        if not current_user.mentor_profile or inv.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if data.intervention_type: inv.intervention_type = data.intervention_type
    if data.recommendation: inv.recommendation = data.recommendation
    if data.reason: inv.reason = data.reason
    if data.priority: inv.priority = data.priority
    if data.status: inv.status = data.status

    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="update_intervention",
            entity_type="intervention",
            entity_id=str(inv.id),
            details=f"Intervention #{inv.id} updated by {current_user.username}",
        )
    )
    db.commit()
    db.refresh(inv)
    return _format_intervention_response(inv)


@router.post("/{intervention_id}/approve", response_model=InterventionResponse)
def approve_intervention(
    intervention_id: int,
    action_req: InterventionActionRequest,
    current_user: User = Depends(require_mentor_or_admin),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """
    Human-in-the-loop: Mentor explicitly APPROVES a proposed intervention.
    Stores audited MentorDecision and converts recommendation into a student task.
    """
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    mentor_id = inv.mentor_id
    if current_user.role == "mentor":
        if not current_user.mentor_profile or inv.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        mentor_id = current_user.mentor_profile.id

    inv.status = "approved"

    # 1. Record MentorDecision
    decision = MentorDecision(
        intervention_id=inv.id,
        mentor_id=mentor_id,
        decision="approved",
        comments=action_req.comments or "Approved following explainable risk review.",
    )
    db.add(decision)

    # 2. Automatically spawn actionable StudentTask
    task_title = f"{inv.intervention_type}: {inv.recommendation[:120]}"
    new_task = StudentTask(
        student_id=inv.student_id,
        course_code="Mentorship",
        source="mentor",
        title=task_title,
        priority=inv.priority,
        status="pending",
        due_date=datetime.now(timezone.utc) + timedelta(days=3),
    )
    db.add(new_task)

    # 3. Audit Log
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="approve_intervention",
            entity_type="intervention",
            entity_id=str(inv.id),
            details=f"Intervention #{inv.id} approved by mentor {current_user.username}. Task spawned.",
        )
    )
    db.commit()
    db.refresh(inv)
    return _format_intervention_response(inv)


@router.post("/{intervention_id}/reject", response_model=InterventionResponse)
def reject_intervention(
    intervention_id: int,
    action_req: InterventionActionRequest,
    current_user: User = Depends(require_mentor_or_admin),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """
    Human-in-the-loop: Mentor REJECTS a proposed intervention with clinical rationale.
    """
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    mentor_id = inv.mentor_id
    if current_user.role == "mentor":
        if not current_user.mentor_profile or inv.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        mentor_id = current_user.mentor_profile.id

    inv.status = "rejected"

    # Record Decision
    decision = MentorDecision(
        intervention_id=inv.id,
        mentor_id=mentor_id,
        decision="rejected",
        comments=action_req.comments or "Rejected based on qualitative mentor assessment.",
    )
    db.add(decision)

    # Audit Log
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="reject_intervention",
            entity_type="intervention",
            entity_id=str(inv.id),
            details=f"Intervention #{inv.id} rejected by mentor {current_user.username}: {action_req.comments}",
        )
    )
    db.commit()
    db.refresh(inv)
    return _format_intervention_response(inv)


@router.post("/{intervention_id}/complete", response_model=InterventionResponse)
def complete_intervention(
    intervention_id: int,
    action_req: InterventionActionRequest,
    current_user: User = Depends(require_mentor_or_admin),
    db: Session = Depends(get_db),
) -> InterventionResponse:
    """Mark an intervention as completed following student meeting or remediation."""
    inv = db.query(Intervention).filter_by(id=intervention_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found.")

    mentor_id = inv.mentor_id
    if current_user.role == "mentor":
        if not current_user.mentor_profile or inv.mentor_id != current_user.mentor_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        mentor_id = current_user.mentor_profile.id

    inv.status = "completed"

    decision = MentorDecision(
        intervention_id=inv.id,
        mentor_id=mentor_id,
        decision="completed",
        comments=action_req.comments or "Completed intervention session successfully.",
    )
    db.add(decision)

    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="complete_intervention",
            entity_type="intervention",
            entity_id=str(inv.id),
            details=f"Intervention #{inv.id} marked as completed by {current_user.username}",
        )
    )
    db.commit()
    db.refresh(inv)
    return _format_intervention_response(inv)
