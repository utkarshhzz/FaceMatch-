"""User model — anyone who can log in (admin or employee)."""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    # Primary key: a unique id Postgres generates for each row.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    full_name: Mapped[str] = mapped_column(String(255), default="")

    # NOTE: we store a HASH, never the plain password. See core/security.py.
    password_hash: Mapped[str] = mapped_column(String(255))

    # "admin" can manage everyone; "employee" is a normal user.
    role: Mapped[str] = mapped_column(String(20), default="employee")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships let us travel between tables in Python:
    #   user.faces  -> list of Face objects
    #   user.attendance -> list of Attendance objects
    # `back_populates` wires the other side of the link.
    faces: Mapped[list["Face"]] = relationship(
        "Face", back_populates="user", cascade="all, delete-orphan"
    )
    attendance: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
