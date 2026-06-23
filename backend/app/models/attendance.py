"""Attendance model — one record per person per day."""
from datetime import datetime, date, timezone

from sqlalchemy import String, DateTime, Date, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # The calendar day this attendance belongs to (UTC date of clock-in).
    date: Mapped[date] = mapped_column(Date, index=True)

    time_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    time_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # present | absent | half_day | leave
    status: Mapped[str] = mapped_column(String(20), default="present")

    # How confident the face match was when this was marked.
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="attendance")

    # Unique constraint: a person can only have ONE attendance row per day.
    # The DB itself rejects a duplicate, which is safer than checking in code.
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date"),
    )
