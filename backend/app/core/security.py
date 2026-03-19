from datetime import datetime,timedelta,timezone
from typing import Any
from jose import JWTError,jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)-> bool:
    return pwd_context.verify(plain_password,hashed_password)

def _build_token(data:dict[str,Any],expires_delta:timedelta)-> str:
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+expires_delta
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)

    
    
def create_access_token(subject:str)->str:
    return _build_token(
        {"sub":subject,"type":"access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        
    )
    
def create_refresh_token(subject:str)->str:
    return _build_token(
        {"sub":subject,"type":"refresh"},
        timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        
    )
    
def decode_token(token:str)-> dict[str,Any]:
    try:
        return jwt.decode(token,settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e