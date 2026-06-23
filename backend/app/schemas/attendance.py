"""Attendance-related Pydantic schemas."""
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel


class MarkAttendanceRequest(BaseModel):
    """LiveAttendance.jsx POSTs { employee_id } after a successful face match."""
    employee_id: str
    confidence: Optional[float] = None


class AttendanceOut(BaseModel):
    id: int
    user_id: int
    date: date
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: str
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class MarkAttendanceResponse(BaseModel):
    """Shape read by LiveAttendance.jsx (it checks `.success` and `.message`)."""
    success: bool
    message: str
    date: Optional[date] = None
    record: Optional[AttendanceOut] = None


class AttendanceAnalytics(BaseModel):
    """Shape read by EmployeeDashboard.jsx analytics cards."""
    attendance_percentage: float = 0.0
    present_days: int = 0
    total_days: int = 0
    current_month_present: int = 0
    current_month_total: int = 0
    absent_days: int = 0
    half_days: int = 0
    leave_days: int = 0
