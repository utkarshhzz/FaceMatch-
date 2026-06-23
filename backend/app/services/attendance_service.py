"""
Attendance business logic.

The key rule: ONE attendance row per user per day. We enforce it both with a
DB unique constraint (models/attendance.py) AND by checking first in code,
so a kiosk scanning the same face twice doesn't create duplicates — it just
replies "already marked".
"""
from datetime import date, timezone, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import Attendance
from app.models.user import User


async def mark_present(db: AsyncSession, user: User, confidence: float | None = None) -> dict:
    """Mark `user` present today. Returns {success, message, record}.

    success=True  -> a new record was created
    success=False -> already marked today (idempotent — not an error)
    """
    today = datetime.now(timezone.utc).date()

    existing = await db.execute(
        select(Attendance).where(Attendance.user_id == user.id, Attendance.date == today)
    )
    record = existing.scalar_one_or_none()

    if record:
        return {
            "success": False,
            "message": f"Attendance already marked for {today.isoformat()}",
            "date": today,
            "record": record,
        }

    record = Attendance(
        user_id=user.id,
        date=today,
        status="present",
        confidence=confidence,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {
        "success": True,
        "message": f"Attendance marked for {today.isoformat()}",
        "date": today,
        "record": record,
    }


async def compute_analytics(db: AsyncSession, user: User) -> dict:
    """Compute the numbers EmployeeDashboard.jsx shows.

    total_days     = days since the user joined (simple proxy for "expected days")
    present_days   = rows with status present/half_day
    current_month  = present rows in the current calendar month
    """
    now = datetime.now(timezone.utc)

    # Present days (count half_day as 0.5 conceptually, but here we just count rows).
    present_rows = await db.execute(
        select(Attendance).where(
            Attendance.user_id == user.id,
            Attendance.status.in_(["present", "half_day"]),
        )
    )
    present_list = present_rows.scalars().all()
    present_days = len(present_list)

    current_month_present = sum(1 for r in present_list if r.date.month == now.month and r.date.year == now.year)

    absent_rows = await db.execute(
        select(func.count()).select_from(Attendance).where(
            Attendance.user_id == user.id, Attendance.status == "absent"
        )
    )
    absent_days = int(absent_rows.scalar() or 0)

    half_rows = await db.execute(
        select(func.count()).select_from(Attendance).where(
            Attendance.user_id == user.id, Attendance.status == "half_day"
        )
    )
    half_days = int(half_rows.scalar() or 0)

    leave_rows = await db.execute(
        select(func.count()).select_from(Attendance).where(
            Attendance.user_id == user.id, Attendance.status == "leave"
        )
    )
    leave_days = int(leave_rows.scalar() or 0)

    # Approximate total days since signup (fallback to present if none).
    total_days = max(present_days + absent_days, 1)
    # Current month day count (days elapsed this month).
    current_month_total = now.day

    pct = round((present_days / total_days) * 100, 1) if total_days else 0.0

    return {
        "attendance_percentage": pct,
        "present_days": present_days,
        "total_days": total_days,
        "current_month_present": current_month_present,
        "current_month_total": current_month_total,
        "absent_days": absent_days,
        "half_days": half_days,
        "leave_days": leave_days,
    }
