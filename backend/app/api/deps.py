#Simple helper functions without Depends

from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import decode_access_token
from app.core.logger import logger


async def get_user_from_token(token):
    """
    Simple function to get user from JWT token.
    No Depends, just pass token directly.
    """
    
    # Decode JWT token
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get email from token
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get database session
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        logger.info(f"User authenticated: {user.email}")
        return user