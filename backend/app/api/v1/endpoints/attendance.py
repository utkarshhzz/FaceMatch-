"""
Attendance endpoints. Mounted under /faces/attendance (the prefix the
frontend hard-codes in LiveAttendance.jsx and EmployeeDashboard.jsx).

mark          (POST) mark attendance by employee_id (after a camera match)
my-records    (GET)  current user's recent attendance
all           (GET)  admin: all records
analytics     (GET)  current user's stats cards
report        (GET)  admin: Excel export
"""
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.attendance import (
    MarkAttendanceRequest,
    MarkAttendanceResponse,
    AttendanceOut,
    AttendanceAnalytics,
)
from app.services.attendance_service import mark_present, compute_analytics

router = APIRouter()


@router.post("/mark", response_model=MarkAttendanceResponse)
async def mark_attendance(
    payload: MarkAttendanceRequest,
    db: AsyncSession = Depends(get_db),
):
    """Mark attendance by employee_id. Called by the kiosk after a face match.

    No token required (kiosk scenario): the employee_id already came from a
    successful face match, which is the auth factor here.
    """
    row = await db.execute(select(User).where(User.employee_id == payload.employee_id))
    user = row.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    result = await mark_present(db, user, confidence=payload.confidence)
    return MarkAttendanceResponse(
        success=result["success"],
        message=result["message"],
        date=result["date"],
        record=AttendanceOut.model_validate(result["record"]) if result.get("record") else None,
    )


@router.get("/my-records", response_model=list[AttendanceOut])
async def my_records(
    limit: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = await db.execute(
        select(Attendance)
        .where(Attendance.user_id == current_user.id)
        .order_by(Attendance.date.desc())
        .limit(limit)
    )
    return rows.scalars().all()


@router.get("/all", response_model=list[AttendanceOut])
async def all_records(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rows = await db.execute(
        select(Attendance).order_by(Attendance.date.desc())
    )
    return rows.scalars().all()


@router.get("/analytics", response_model=AttendanceAnalytics)
async def my_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await compute_analytics(db, current_user)
    return AttendanceAnalytics(**data)


@router.get("/report")
async def export_report(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Export ALL attendance as an .xlsx file (AdminDashboard.jsx downloads blob)."""
    try:
        from openpyxl import Workbook
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl not installed on server")

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"
    ws.append(["Employee ID", "Employee Name", "Email", "Date", "Time In", "Status", "Confidence"])

    # Join attendance -> user in Python (simple; fine for moderate sizes).
    att_rows = await db.execute(select(Attendance).order_by(Attendance.date.desc()))
    for att in att_rows.scalars().all():
        u_row = await db.execute(select(User).where(User.id == att.user_id))
        u = u_row.scalar_one_or_none()
        ws.append([
            u.employee_id if u else "",
            u.full_name if u else "",
            u.email if u else "",
            att.date.isoformat() if att.date else "",
            att.time_in.strftime("%Y-%m-%d %H:%M:%S") if att.time_in else "",
            att.status,
            att.confidence,
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f"attendance_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
