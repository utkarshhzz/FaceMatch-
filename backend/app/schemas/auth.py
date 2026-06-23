"""Auth-related Pydantic schemas."""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = ""
    employee_id: Optional[str] = None
    role: str = "employee"   # admin can promote later


class LoginRequest(BaseModel):
    """The frontend sends EITHER email or employee_id (see Login.jsx).
    We make both optional and validate in the route."""
    email: Optional[EmailStr] = None
    employee_id: Optional[str] = None
    password: str


class TokenResponse(BaseModel):
    """Exactly what the frontend stores: AuthContext.jsx saves
    `response.data.access_token` to localStorage."""
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    """Shape of a user returned to the frontend (never include password!)."""
    id: int
    email: EmailStr
    employee_id: Optional[str] = None
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class AdminResetPasswordRequest(BaseModel):
    """Admin resets another user's password."""
    target_email: Optional[EmailStr] = None
    target_employee_id: Optional[str] = None
    new_password: str = Field(min_length=6)


# Resolve forward reference ("UserOut" string above) at import time.
TokenResponse.model_rebuild()
