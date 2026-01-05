from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional
from enum import Enum


class AttendanceStatusEnum(str, Enum):
    """Attendance status enum for schemas"""
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"


class AttendanceMarkRequest(BaseModel):
    """Request schema for marking attendance"""
    user_id: int


class AttendanceResponse(BaseModel):
    """Response schema for attendance records"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: AttendanceStatusEnum
    created_at: datetime
    updated_at: datetime


class AttendanceMarkResponse(BaseModel):
    """Response schema for attendance marking"""
    success: bool
    message: str
    attendance: Optional[AttendanceResponse] = None


class AttendanceAnalytics(BaseModel):
    """Schema for attendance analytics"""
    total_days: int
    present_days: int
    absent_days: int
    half_days: int
    leave_days: int
    attendance_percentage: float
    current_month_present: int
    current_month_total: int
