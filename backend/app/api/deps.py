from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.models.academic import Student, Mentor

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and authenticate user via Bearer JWT."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired, invalid, or forged.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identity.",
        )
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with this token does not exist.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact institutional administration.",
        )
    return user


def require_role(allowed_roles: List[str]):
    """Role-based authorization dependency factory."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Operation requires one of the roles {allowed_roles}. Current role: '{current_user.role}'.",
            )
        return current_user
    return role_checker

require_student = require_role(["student"])
require_mentor = require_role(["mentor"])
require_admin = require_role(["admin"])
require_mentor_or_admin = require_role(["mentor", "admin"])


def enforce_student_isolation(current_user: User, target_student_id: int, db: Session) -> Student:
    """
    Ensure a student can ONLY access their own records.
    Admin users can access any student record.
    """
    target = db.query(Student).filter_by(id=target_student_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record with ID {target_student_id} not found.",
        )
    if current_user.role == "admin":
        return target
    if current_user.role == "student":
        if not current_user.student_profile or current_user.student_profile.id != target_student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security violation: You cannot access or view another student's academic records.",
            )
        return target
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized access to student record.",
    )


def enforce_mentor_isolation(current_user: User, target_student_id: int, db: Session) -> Student:
    """
    Ensure a mentor can ONLY access their assigned mentees.
    Admin users can access any student record.
    """
    target = db.query(Student).filter_by(id=target_student_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record with ID {target_student_id} not found.",
        )
    if current_user.role == "admin":
        return target
    if current_user.role == "mentor":
        mentor_profile = current_user.mentor_profile
        if not mentor_profile or target.mentor_id != mentor_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security violation: This student is not assigned to your mentorship cohort.",
            )
        return target
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized access to student record.",
    )
