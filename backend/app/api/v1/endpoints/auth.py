"""
Authentication endpoints.

register        -> create a new user (hashes the password with bcrypt)
login           -> verify creds, return a JWT access token (+ user object)
me              -> return the currently logged-in user (uses get_current_user)
admin-reset     -> admin resets another user's password
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
    AdminResetPasswordRequest,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Create a user. We auto-generate an employee_id if none is supplied."""
    # Uniqueness checks: reject duplicate email / employee_id up front.
    existing = await db.execute(
        select(User).where(or_(User.email == payload.email,
                               User.employee_id == payload.employee_id if payload.employee_id else False))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email or employee_id already registered")

    employee_id = payload.employee_id or _generate_employee_id(payload.email)

    user = User(
        email=payload.email,
        employee_id=employee_id,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),   # bcrypt hash, never plaintext
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login by email OR employee_id (matches the frontend logic)."""
    if not payload.email and not payload.employee_id:
        raise HTTPException(status_code=422, detail="Provide email or employee_id")

    # Build a flexible query: match on whichever identifier was supplied.
    condition = User.email == payload.email if payload.email else User.employee_id == payload.employee_id
    result = await db.execute(select(User).where(condition))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        # Same error for "no such user" and "wrong password" — do NOT leak
        # which one it was (a small but real security practice).
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/admin/reset-password", response_model=UserOut)
async def admin_reset_password(
    payload: AdminResetPasswordRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin resets a user's password (see Part F for the full explanation
    of WHY we can only reset, never recover, a bcrypt password)."""
    condition = (
        User.email == payload.target_email if payload.target_email
        else User.employee_id == payload.target_employee_id
    )
    result = await db.execute(select(User).where(condition))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    user.password_hash = hash_password(payload.new_password)
    await db.commit()
    await db.refresh(user)
    return user


def _generate_employee_id(email: str) -> str:
    """Tiny helper: make a numeric employee_id from the email when none given."""
    import hashlib
    return str(int(hashlib.md5(email.encode()).hexdigest(), 16) % 1_000_000_000).zfill(9)
