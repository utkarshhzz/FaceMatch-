"""
Authentication endpoints - Simple version without Depends
"""

from fastapi import APIRouter, HTTPException, status, Header
from sqlalchemy import select

from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token, validate_password_strength
from app.api.deps import get_user_from_token
from app.db.session import AsyncSessionLocal
from app.core.logger import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    Simple version: Just pass data directly, no Depends!
    """
    
    # Create database session directly
    async with AsyncSessionLocal() as db:
        
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.USER,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
        
        return new_user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login with email and password.
    
    Simple version: Direct database access, no Depends!
    """
    
    # Create database session directly
    async with AsyncSessionLocal() as db:
        
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        # Check if user exists
        if not user:
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(authorization: str = Header(None)):
    """
    Get current authenticated user information.
    
    Simple version: Pass token in header directly!
    
    Header: Authorization: Bearer YOUR_TOKEN_HERE
    """
    
    # Check if Authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer TOKEN"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Get user from token (using our helper function)
    user = await get_user_from_token(token)
    
    return user
