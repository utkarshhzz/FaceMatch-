##importing all models here for easy access

from app.models.user import User,UserRole
from app.models.face import Face
from app.models.encoding import Encoding
from app.models.audit_log import AuditLog
from app.models.attendance import Attendance, AttendanceStatus

## Export all models

__all__=["User","UserRole","Face","Encoding","AuditLog","Attendance","AttendanceStatus"]

