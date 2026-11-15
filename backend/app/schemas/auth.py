from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

try:
    import email_validator  # noqa: F401
    from pydantic import EmailStr
except (ImportError, Exception):
    EmailStr = str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: str
    expires_in: int
    user: Optional[Dict[str, Any]] = None

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    username: str = Field(..., description="Student Reg No, Faculty ID (e.g. m08), or Admin username/email")
    password: str = Field(..., description="User password")
    role_hint: Optional[str] = Field(None, description="Optional role hint from login tabs: student, mentor, admin")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    profile: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Username or email of the account")

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=6)
