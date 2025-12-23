##Encoding model stores face embeddings (512 dim vectors)

from sqlalchemy import Column,Integer,ForeignKey,LargeBinary,String
from sqlalchemy.orm import relationship

from app.db.base import Base,TimestampMixin


class Encoding(Base,TimestampMixin):
    __tablename__="encodings"
    
    id=Column(Integer,primary_key=True,index=True)
    face_id=Column(Integer,ForeignKey("faces.id"),unique=True,nullable=False,index=True)
    
    #Store embedding as binary data(more efficient than json)
    embedding=Column(LargeBinary,nullable=False)  ##Numpy array serialised
    
    #model metadata
    model_name=Column(String(50),default="arcface")
    model_version=Column(String(20))
    
    #relationships
    face=relationship("Face",back_populates="encoding")
    
    def __repr__(self):
        return f"<Encoding(id={self.id}, face_id={self.face_id})>"
