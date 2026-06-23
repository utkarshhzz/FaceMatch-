"""
Face management endpoints. Mounted under /faces.

register          (POST)   register/upload a face photo + embedding
match             (POST)   match an uploaded photo against all known faces
match-camera      (POST)   same as match (used by the live camera kiosk)
my-faces          (GET)    list the current user's registered faces
delete            (DELETE) delete one of the current user's faces
employees         (GET)    admin: list all employees
employees/{id}    (DELETE) admin: delete an employee (cascade)
attendance/...    included from attendance.py under the same prefix

NOTE on async + CPU work:
  InsightFace is synchronous and CPU-heavy. We wrap every call in
  `asyncio.to_thread(...)` so the heavy numpy work runs in a worker thread
  and the FastAPI event loop can keep serving other requests meanwhile.
"""
import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import app_logger
from app.core.security import hash_password
from app.models.user import User
from app.models.face import Face, FaceEncoding
from app.schemas.face import (
    RegisterFaceResponse,
    MatchFaceResponse,
    FaceOut,
    EmployeeOut,
    MessageResponse,
)
from app.services import face_service
from app.utils.image import decode_image, assess_quality

router = APIRouter()


# ---------- helpers ----------
async def _read_and_decode(file: UploadFile):
    """Read upload bytes, validate size, decode to a BGR numpy image."""
    data = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.MAX_FILE_SIZE_MB}MB)")

    img = decode_image(data)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use JPG/PNG.")
    return img


async def _async_quality(img):
    return await asyncio.to_thread(assess_quality, img)


async def _async_embedding(img):
    return await asyncio.to_thread(face_service.generate_embedding, img)


# ---------- REGISTER ----------
@router.post("/register", response_model=RegisterFaceResponse, status_code=status.HTTP_201_CREATED)
async def register_face(
    file: UploadFile = File(...),
    employee_id: str = Form(...),
    full_name: str = Form(""),
    email: str | None = Form(None),
    photo_number: int = Form(1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a face. Find-or-create the employee, then store embedding."""
    img = await _read_and_decode(file)

    # Quality gate (non-fatal warnings: we still proceed, but report metrics).
    quality = await _async_quality(img)

    # Run the AI model in a threadpool to avoid blocking the server.
    embedding = await _async_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in the image.")

    # Find or create the employee user.
    result = await db.execute(select(User).where(User.employee_id == employee_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Auto-create the user (admin is registering a new employee).
        if not email:
            raise HTTPException(status_code=400, detail="email is required when registering a new employee")
        # Avoid email collision.
        dup = await db.execute(select(User).where(User.email == email))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="An account with this email already exists")

        user = User(
            email=email,
            employee_id=employee_id,
            full_name=full_name or employee_id,
            password_hash=hash_password(str(uuid.uuid4())),  # random; admin resets later
            role="employee",
        )
        db.add(user)
        await db.flush()  # gives us user.id without committing
    else:
        # Enforce per-user max faces.
        count_row = await db.execute(
            select(func.count()).select_from(Face).where(Face.user_id == user.id)
        )
        if int(count_row.scalar() or 0) >= settings.MAX_FACES_PER_USER:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum of {settings.MAX_FACES_PER_USER} faces per employee reached.",
            )

    # Save the original photo (optional) + DB rows.
    image_path = None
    try:
        import os
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        fname = f"{user.id}_{photo_number}_{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(settings.UPLOAD_DIR, fname)
        import cv2
        await asyncio.to_thread(lambda: cv2.imwrite(image_path, img))
    except Exception as e:  # noqa: BLE001
        app_logger.warning("Could not save upload: {}", e)
        image_path = None

    face = Face(
        user_id=user.id,
        photo_number=photo_number,
        blur_score=quality["blur_score"],
        brightness=quality["brightness"],
        image_path=image_path,
    )
    db.add(face)
    await db.flush()

    encoding = FaceEncoding(
        face_id=face.id,
        embedding_json=face_service.embedding_to_json(embedding),
        norm=float((embedding @ embedding) ** 0.5),
    )
    db.add(encoding)
    await db.commit()
    await db.refresh(face)

    app_logger.info("Registered face id={} for employee_id={}", face.id, employee_id)

    return RegisterFaceResponse(
        message=f"Face registered successfully for {user.full_name}",
        face_id=face.id,
        user_id=user.id,
        employee_id=user.employee_id,
        full_name=user.full_name,
        quality=quality,
    )


# ---------- MATCH (shared by /match and /match-camera) ----------
async def _do_match(img, db: AsyncSession) -> MatchFaceResponse:
    """Run detection + embedding + DB-wide cosine match."""
    embedding = await _async_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in the image.")

    # Load every stored embedding. (For large orgs you'd cache this in Redis;
    # see services/cache.py — kept simple here for clarity.)
    rows = await db.execute(
        select(FaceEncoding.id, FaceEncoding.embedding_json)
    )
    stored = [(r[0], r[1]) for r in rows.all()]

    match = face_service.match_against_all(embedding, stored, settings.MATCHING_THRESHOLD)

    if not match["matched"] or match["best_encoding_id"] is None:
        return MatchFaceResponse(
            match_found=False,
            message="No matching face found in the database.",
            confidence=round(match["confidence"], 4),
            distance=round(match["distance"], 4),
        )

    # Resolve the matched encoding -> face -> user.
    enc_row = await db.execute(
        select(FaceEncoding).where(FaceEncoding.id == match["best_encoding_id"])
    )
    enc = enc_row.scalar_one_or_none()
    face_row = await db.execute(select(Face).where(Face.id == enc.face_id))
    face = face_row.scalar_one_or_none()
    user_row = await db.execute(select(User).where(User.id == face.user_id))
    user = user_row.scalar_one_or_none()

    return MatchFaceResponse(
        match_found=True,
        full_name=user.full_name,
        employee_id=user.employee_id,
        user_id=user.id,
        confidence=round(match["confidence"], 4),
        distance=round(match["distance"], 4),
        message=f"Matched {user.full_name} ({(match['confidence']*100):.1f}% confidence)",
    )


@router.post("/match", response_model=MatchFaceResponse)
async def match_face(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Match an uploaded photo against the database."""
    img = await _read_and_decode(file)
    return await _do_match(img, db)


@router.post("/match-camera", response_model=MatchFaceResponse)
async def match_camera(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Kiosk endpoint: the live-attendance camera calls this.
    Auth-free so a shared kiosk browser (no login) can mark attendance —
    the matched employee_id is then verified on the attendance endpoint."""
    img = await _read_and_decode(file)
    return await _do_match(img, db)


# ---------- MY FACES ----------
@router.get("/my-faces", response_model=list[FaceOut])
async def my_faces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = await db.execute(select(Face).where(Face.user_id == current_user.id))
    return rows.scalars().all()


@router.delete("/{face_id}", response_model=MessageResponse)
async def delete_face(
    face_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = await db.execute(select(Face).where(Face.id == face_id))
    face = row.scalar_one_or_none()
    if face is None:
        raise HTTPException(status_code=404, detail="Face not found")
    # Only the owner (or an admin) may delete.
    if face.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    await db.delete(face)
    await db.commit()
    return MessageResponse(message="Face deleted")


# ---------- ADMIN: employees ----------
@router.get("/employees", response_model=list[EmployeeOut])
async def list_employees(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """AdminDashboard.jsx reads `.employees` with fields:
    id, employee_id, full_name, is_active, faces_count."""
    users = await db.execute(select(User).order_by(User.full_name))
    out = []
    for u in users.scalars().all():
        count_row = await db.execute(
            select(func.count()).select_from(Face).where(Face.user_id == u.id)
        )
        faces_count = int(count_row.scalar() or 0)
        out.append(EmployeeOut(
            id=u.id,
            employee_id=u.employee_id,
            full_name=u.full_name,
            email=u.email,
            is_active=u.is_active,
            faces_count=faces_count,
        ))
    return out


@router.delete("/employees/{employee_id}", response_model=MessageResponse)
async def delete_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete an employee by employee_id (cascade removes faces/encodings)."""
    row = await db.execute(select(User).where(User.employee_id == employee_id))
    user = row.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    await db.delete(user)
    await db.commit()
    return MessageResponse(message=f"Employee {employee_id} deleted")


# Attendance sub-routes are added in router.py under this same prefix.
