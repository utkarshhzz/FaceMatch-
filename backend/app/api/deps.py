"""
Shared FastAPI dependencies.

get_db          -> gives a route a database session.
get_current_user-> authenticates a Bearer token and returns the User row.
require_admin   -> same as above, but also enforces role == "admin".

These let protected routes be ONE line:
    async def me(current_user: User = Depends(get_current_user)): ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# `tokenUrl` is just metadata for the Swagger "Authorize" button — it points
# at where a user would log in to get a token. auto_error=False lets us
# return a custom message instead of an automatic 401 when no token is sent.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.APP_V1_PREFIX}/auth/login", auto_error=False
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT, find the user it belongs to, return that User.

    Flow:
      1. No token?  -> 401
      2. Decode JWT -> fails? 401 (invalid/expired)
      3. `sub` claim holds the user id -> look it up
      4. User not found / inactive? -> 401
    """
    creds_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise creds_error

    try:
        payload = decode_token(token)
    except ValueError:
        raise creds_error

    # We store the user id in the "sub" (subject) claim when creating tokens.
    user_id_str = payload.get("sub")
    token_type = payload.get("type")
    if not user_id_str or token_type != "access":
        raise creds_error

    try:
        user_id = int(user_id_str)
    except (TypeError, ValueError):
        raise creds_error

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise creds_error

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Same as get_current_user, but only 'admin' role may pass."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
