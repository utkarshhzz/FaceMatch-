##Audit log to track all system actios

from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime,ForeignKey
from datetime import datetime

from app.db.base import Base

class AuditLog(Base):
    __tablename__="audit_logs"
    
    id=Column(Integer,primary_key=True,index=True)
    
    #whodid it
    user_id=Column(Integer,ForeignKey("users.id"),nullable=True,index=True)
    
    #what happend
    action= Column(String(150),nullable=False,index=True)
    resource_type=Column(String(100),nullable=False)
    resource_id=Column(Integer,nullable=True,index=True)
    
    
    #details
    details=Column(Text)   #JSON string with extra info
    ip_address=Column(String(50))
    user_agent=Column(String(500))
    
    
    #when
    timestamp=Column(DateTime,default=datetime.utcnow,index=True,nullable=False)
    
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action})>"