from datetime import datetime,timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError,jwt

from app.core.config import settings
from app.core.logger import logger

#password hashing (one way)

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password):
    
    return pwd_context.hash(password)


def verify_password(plain_password,hashed_password):
    try:
        return pwd_context.verify(plain_password,hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed:{e}")
        return False
    
def create_access_token(data,expires_delta=None):
    to_encode=data.copy()
    
    if expires_delta:
        expire=datetime.utcnow()+expires_delta
    else:
        expire=datetime.utcnow()+ timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt= jwt.encode(to_encode,
                            settings.SECRET_KEY,
                            algorithm=settings.ALGORITHM)
    logger.info("Access token created ",extra={"expires_at": expire.isoformat()})
    return encoded_jwt

def decode_access_token(token):
    try:
        payload=jwt.decode(token,
                           settings.SECRET_KEY,
                           algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed {e}")
        return None
    except Exception as e:
        logger.error(f" Unexpected error while decoding the token {e}")
        return None
    
    
def validate_password_strength(password):
    if len(password) < 8:
        return False,"Password must be 8 characters long"
    if not any(char.isupper() for char in password):
        return False,"Password must contain atleast one uppercase character"
    
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    return True, None

def create_password_reset_token(email):
    expires= timedelta(hours=1)
    return create_access_token(data={"sub":email,"type":"password_reset"},
                               expires_delta=expires)

def verify_password_reset_token(token):
    payload=decode_access_token(token)
    
    if not payload:
        return None
    if payload.get("type") != "password_reset":
        logger.warning("Invalid token type for passowrd reset")
        return None
    return payload.get("sub")
