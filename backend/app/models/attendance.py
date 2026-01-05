from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class AttendanceStatus(enum.Enum):
    """Attendance status enum"""
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"


class Attendance(Base):
    """Attendance model for tracking employee attendance"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.date}, status={self.status})>"
