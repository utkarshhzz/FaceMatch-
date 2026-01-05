#User model -> stores suer accounts

from sqlalchemy import Column,Integer,String,Boolean,Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base,TimestampMixin


class UserRole(enum.Enum):
    USER="user"
    ADMIN="admin"
    MODERATOR="moderator"
    
class User(Base,TimestampMixin):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    employee_id=Column(String(50),unique=True,index=True,nullable=False)  # Unique employee ID
    full_name=Column(String(255),nullable=False)
    email=Column(String(100),unique=True,index=True,nullable=False)
    hashed_password=Column(String(255),nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
    is_verified=Column(Boolean,default=False,nullable=False)
    role=Column(SQLEnum(UserRole),default=UserRole.USER,nullable=False)
    
    #Relationships
    faces=relationship("Face",back_populates="user",cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id},employee_id={self.employee_id},email={self.email})>"