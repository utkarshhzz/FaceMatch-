"""
Top-level API router. Assembles all endpoint groups under /api/v1.

The faces router also mounts the attendance router under /faces/attendance so
the URLs match exactly what the frontend hard-codes:
    GET  /faces/attendance/analytics   (EmployeeDashboard.jsx)
    GET  /faces/attendance/my-records  (EmployeeDashboard.jsx)
    POST /faces/attendance/mark        (LiveAttendance.jsx)
    GET  /faces/attendance/report      (AdminDashboard.jsx)
"""
from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.faces import router as faces_router
from app.api.v1.endpoints.attendance import router as attendance_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(faces_router, prefix="/faces", tags=["Faces"])

# Attendance lives UNDER /faces so frontend URLs are unchanged.
faces_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
