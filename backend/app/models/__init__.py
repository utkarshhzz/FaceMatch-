"""ORM models package. Importing models here registers them with Base.metadata
so create_all() knows about every table."""
from app.models.user import User
from app.models.face import Face, FaceEncoding
from app.models.attendance import Attendance

__all__ = ["User", "Face", "FaceEncoding", "Attendance"]
