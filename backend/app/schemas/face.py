#face related schemas

from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class FaceUploadResponse(BaseModel):
    """Response after uplaoding the face"""
    id: int
    user_id: int
    quality_score:float
    is_blurry: bool
    brightness_score: float
    detection_confidence: float
    is_primary:bool
    created_at:datetime
    
    class Config:
        from_attributes= True
        
        
class FaceMatchResult(BaseModel):
    """Single match result"""
    user_id: int
    user_email:str
    user_name:Optional[str]
    face_id:int
    similarity:float
    quality_score:float
    
class FaceMatchResponse(BaseModel):
    """Response for face matching"""
    match_found:bool
    employee_id:Optional[str]=None
    full_name:Optional[str]=None
    confidence:Optional[float]=None
    message: str
    
    
class FaceDetailResponse(BaseModel):
    """Detailed face information"""
    id: int
    user_id: int
    original_image_path: Optional[str]
    processed_image_path: Optional[str]
    quality_score: float
    is_blurry: bool
    brightness: float
    face_size: int
    is_primary: bool
    created_at: datetime
    updated_at: datetime
    
    
class FaceRegisterResponse(BaseModel):
    success: bool
    message: str
    employee_id: str
    face_id: int
    image_url: str
    
    class Config:
        from_attributes = True