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
    matched:bool
    best_match:Optional[FaceMatchResult]
    all_matches:List[FaceMatchResult]
    threshold:float=0.6
    
    
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
    
    class Config:
        from_attributes = True