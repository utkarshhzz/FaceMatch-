"""Face + FaceEncoding models.

A Face  = one registered photo of a person (they may have several).
A FaceEncoding = the 512-number vector the AI extracted from that photo.
                This vector is what we actually compare at match time.
"""
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Face(Base):
    __tablename__ = "faces"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key: this column holds the id of a row in `users`.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Front=1, left=2, right=3 ... (informational)
    photo_number: Mapped[int] = mapped_column(default=1)

    # Quality metrics from the image check (helps debugging / UI display).
    blur_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brightness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Where we saved the original uploaded photo (optional, for reference).
    image_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Back-reference to the owning user, and the one-to-one encoding.
    user: Mapped["User"] = relationship("User", back_populates="faces")
    encoding: Mapped[Optional["FaceEncoding"]] = relationship(
        "FaceEncoding", back_populates="face", uselist=False, cascade="all, delete-orphan"
    )


class FaceEncoding(Base):
    __tablename__ = "face_encodings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    face_id: Mapped[int] = mapped_column(ForeignKey("faces.id", ondelete="CASCADE"), unique=True)

    # ArcFace produces a 512-float vector. We store it as a JSON string so it
    # works on any DB. (We convert list <-> str when reading/writing.)
    embedding_json: Mapped[str] = mapped_column(Text)

    # Norm so we can re-use it for cosine similarity quickly.
    norm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    face: Mapped["Face"] = relationship("Face", back_populates="encoding")
