#User related schemas
from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime


#Base Schema
class UserBase(BaseModel):
    email:EmailStr
    full_name:Optional[str]=None
    
#Schema for user registration
class UserCreate(UserBase):
    password: str= Field(...,min_length=8,description="Password must be at least 8 characters long")
 
 #Schema for user login
class UserLogin(BaseModel):
    email:EmailStr
    password:str
    
    
#Schema for user response
class UserResponse(UserBase):
    id:int
    is_active:bool
    is_verified: bool
    role:str
    created_at: datetime
    
    class config:
        from_attributes= True
        
#Schema for jwt toke response
class Token(BaseModel):
    access_token:str
    token_type:str="bearer"
    
    
#Schema for token data

class TokenData(BaseModel):
    email:Optional[str] =None