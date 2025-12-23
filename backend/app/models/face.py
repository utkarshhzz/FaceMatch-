##face model-->> stores face images and metadata

from sqlalchemy import Column,Integer,String,Float,Boolean,ForeignKey,Text
from sqlalchemy.orm import relationship

from app.db.base import Base,TimestampMixin


class Face(Base,TimestampMixin):
    __tablename__="faces"
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    
    ##File storage
    original_image_path=Column(String(500))
    processed_image_path=Column(String(500))
    
    ##Face detection metadata
    detection_confidence=Column(Float)
    face_box=Column(Text)     #JSON string: {x,y,width,height}
    
    ##Quality metrics
    quality_score=Column(Float)
    is_blurry=Column(Boolean,default=False)
    brightness_score=Column(Float)
    
    is_primary=Column(Boolean,default=False)  ##main face fort he user
    
    #Relationships
    user= relationship("User",back_populates="faces")
    encoding=relationship("Encoding",back_populates="face",uselist=False,cascade="all, delete-orphan")
    
    def __repr__(self):
         return f"<Face(id={self.id}, user_id={self.user_id})>" 