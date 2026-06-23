"""Face-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class FaceOut(BaseModel):
    id: int
    user_id: int
    photo_number: int
    blur_score: Optional[float] = None
    brightness: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeOut(BaseModel):
    """Shape returned by GET /faces/employees (AdminDashboard.jsx reads these)."""
    id: int
    employee_id: str
    full_name: str
    email: str
    is_active: bool
    faces_count: int = 0

    model_config = {"from_attributes": True}


class RegisterFaceResponse(BaseModel):
    message: str
    face_id: int
    user_id: int
    employee_id: str
    full_name: str
    quality: dict


class MatchFaceResponse(BaseModel):
    """Shape read by MatchFace.jsx / LiveAttendance.jsx.
    They check `match_found`, `full_name`, `employee_id`, `confidence`."""
    match_found: bool
    full_name: str = "Unknown"
    employee_id: Optional[str] = None
    user_id: Optional[int] = None
    confidence: float = 0.0     # 0..1 (similarity, higher = better)
    distance: float = 1.0       # raw cosine distance (lower = better)
    message: str = ""


class MessageResponse(BaseModel):
    message: str
