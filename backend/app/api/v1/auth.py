from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.core.config import settings
from backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from backend.app.models.user import User
from backend.app.models.system import AuditLog
from backend.app.schemas.auth import (
    Token,
    LoginRequest,
    UserResponse,
    UserProfileUpdate,
    PasswordChangeRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate user credentials across Student, Mentor, and Admin roles.
    Supports login via username or email.
    """
    identifier = login_data.username.strip()
    user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )

    if not user or not verify_password(login_data.password, user.password_hash):
        # Record failed attempt audit
        db.add(
            AuditLog(
                actor_role="anonymous",
                action="login_failure",
                entity_type="user",
                entity_id=identifier,
                details=f"Invalid credentials submitted for identifier: {identifier}",
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive. Please contact administration.",
        )

    # Optional role validation if role hint provided
    if login_data.role_hint and login_data.role_hint.lower() != user.role.lower():
        # Notice: warn or permit, but return the user's authentic database role
        pass

    access_token = create_access_token(
        subject=user.username,
        role=user.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Record successful login audit
    db.add(
        AuditLog(
            user_id=user.id,
            actor_role=user.role,
            action="login_success",
            entity_type="user",
            entity_id=str(user.id),
            details=f"Session established for {user.username} ({user.role})",
        )
    )
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        username=user.username,
        full_name=user.full_name,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email,
        },
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Terminate current user session."""
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="logout",
            entity_type="user",
            entity_id=str(current_user.id),
            details=f"Session terminated for {current_user.username}",
        )
    )
    db.commit()
    return {"message": "Session terminated successfully.", "status": "logged_out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return profile and metadata of the currently authenticated user."""
    profile_data = {}
    if current_user.role == "student" and current_user.student_profile:
        stu = current_user.student_profile
        profile_data = {
            "student_id": stu.id,
            "registration_number": stu.registration_number,
            "section": stu.section,
            "semester": stu.semester,
            "department": stu.department,
            "programme": stu.programme,
            "mentor_id": stu.mentor_id,
            "academic_status": stu.academic_status,
            "sem2_sgpa": stu.sem2_sgpa,
            "cgpa_band": stu.cgpa_band,
        }
    elif current_user.role == "mentor" and current_user.mentor_profile:
        men = current_user.mentor_profile
        profile_data = {
            "mentor_id": men.id,
            "faculty_code": men.faculty_code,
            "department": men.department,
            "designation": men.designation,
            "workload_cap": men.workload_cap,
            "assigned_mentees_count": len(men.students),
        }
    elif current_user.role == "admin":
        profile_data = {
            "admin_scope": "Institutional Super Administrator",
            "access_level": "Full",
        }

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profile=profile_data,
    )


@router.put("/profile", response_model=UserResponse)
def update_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update profile information for the current user."""
    if update_data.full_name:
        current_user.full_name = update_data.full_name.strip()
    if update_data.email:
        # Check if email is already taken
        existing = (
            db.query(User)
            .filter(User.email == update_data.email, User.id != current_user.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already in use by another account.",
            )
        current_user.email = update_data.email.strip()

    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="update_profile",
            entity_type="user",
            entity_id=str(current_user.id),
            details=f"Profile updated for {current_user.username}",
        )
    )
    db.commit()
    db.refresh(current_user)
    return get_me(current_user)


@router.post("/change-password")
def change_password(
    pwd_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Change user password after verifying the old password."""
    if not verify_password(pwd_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed.",
        )
    current_user.password_hash = get_password_hash(pwd_data.new_password)
    db.add(
        AuditLog(
            user_id=current_user.id,
            actor_role=current_user.role,
            action="password_change",
            entity_type="user",
            entity_id=str(current_user.id),
            details=f"Password changed successfully for {current_user.username}",
        )
    )
    db.commit()
    return {"message": "Password changed successfully."}


@router.post("/forgot-password")
def forgot_password(
    req: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Initiate password recovery workflow and generate a password reset token."""
    identifier = req.identifier.strip()
    user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )
    if not user:
        # Return generic message to prevent username enumeration
        return {
            "message": "If an account matching the provided identifier exists, recovery instructions have been initiated.",
            "status": "initiated",
        }

    # Generate a temporary password reset token valid for 30 minutes
    reset_token = create_access_token(
        subject=f"reset:{user.username}",
        role="password_reset",
        expires_delta=timedelta(minutes=30),
    )

    db.add(
        AuditLog(
            user_id=user.id,
            actor_role="system",
            action="password_reset_request",
            entity_type="user",
            entity_id=str(user.id),
            details=f"Reset token generated for {user.username}",
        )
    )
    db.commit()

    return {
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token,
        "expires_in_minutes": 30,
        "note": "In production, this token is dispatched securely via institutional email.",
    }


@router.post("/reset-password")
def reset_password(
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Complete password recovery using a valid reset token."""
    payload = decode_access_token(req.reset_token)
    if not payload or payload.get("role") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    sub = payload.get("sub", "")
    if not sub.startswith("reset:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed reset token subject.",
        )
    username = sub.replace("reset:", "")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user account does not exist.",
        )

    user.password_hash = get_password_hash(req.new_password)
    db.add(
        AuditLog(
            user_id=user.id,
            actor_role="system",
            action="password_reset_complete",
            entity_type="user",
            entity_id=str(user.id),
            details=f"Password reset completed for {user.username}",
        )
    )
    db.commit()
    return {"message": "Password reset completed successfully. You may now log in with your new credentials."}
