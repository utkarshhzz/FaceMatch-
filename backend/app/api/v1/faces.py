### Fae recongnition endpoints

from tkinter.font import Font
from fastapi import Depends,APIRouter,UploadFile,File,Header,HTTPException,status,Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from typing import Optional

from app.schemas.face import (
    FaceDetailResponse,
    FaceUploadResponse,
    FaceMatchResponse,
    FaceMatchResult,
    FaceRegisterResponse
)

from app.models.user import User, UserRole
from app.models.face import Face
from app.models.encoding import Encoding
from app.core.security import decode_access_token
from app.core.logger import logger
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.utils.face_detector import face_detector
from app.utils.face_encoder import face_encoder

router=APIRouter(prefix="/faces",tags=["Face Recognition"])

#helper function to get current user
async def get_current_user_from_token(authorization:str) -> User:
    """extracting and validating user from JWT token"""
    logger.info(f"Received authorization header: {authorization}")
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning(f"Invalid authorization format: {authorization}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    token=authorization.replace("Bearer ","")
    payload=decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
        
    email=payload.get("sub")
    
    async with AsyncSessionLocal() as db:
        result=await db.execute(select(User).where(User.email==email))
        user=result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    
@router.post("/register",response_model=FaceRegisterResponse)
async def register_face(
    employee_id:str=Form(...),
    full_name: str= Form(...),
    file:UploadFile=File(...),
    authorization:str=Header(None)
):
    """Upload and register a face image for an employee (Admin only)
    Admin provides employee_id, full_name, and face photo
    System creates or finds the employee user and registers their face
    """
    
    #Get current admin user
    admin_user=await get_current_user_from_token(authorization)
    
    # Check if user is admin
    if admin_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can register employee faces"
        )
    
    #validation
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Find or create employee user
        async with AsyncSessionLocal() as db:
            # Check if employee already exists
            result = await db.execute(
                select(User).where(User.employee_id == employee_id)
            )
            employee_user = result.scalar_one_or_none()
            
            if not employee_user:
                # Create new employee user with temporary email and password
                from app.core.security import hash_password
                employee_user = User(
                    employee_id=employee_id,
                    full_name=full_name,
                    email=f"{employee_id}@temp.local",  # Temporary email
                    hashed_password=hash_password("changeme123"),  # Temporary password
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=False
                )
                db.add(employee_user)
                await db.commit()
                await db.refresh(employee_user)
                logger.info(f"Created new employee user: {employee_id}")
        
        #creating upload directory for this employee
        upload_dir=f"./data/uploads/{employee_user.id}"
        os.makedirs(upload_dir,exist_ok=True)
        
        #generating unique filename
        file_extension=file.filename.split(".")[-1]
        unique_filename=f"{uuid.uuid4()}.{file_extension}"
        file_path=os.path.join(upload_dir,unique_filename)
        
        #save the file at the location
        with open(file_path,'wb') as f:
            content=await file.read()
            f.write(content)
            
        logger.info(f"Saved uploaded image to {file_path}")
        
        
        #Face detection and quality check
        face_info=face_detector.detect_face(file_path)
        if not face_info:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
        #Checking quality
        if face_info['quality_score'] <0.5:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face quality too low: {face_info['quality_score']:.2f}"
            )
        
        #Extract embedding
        embedding=face_encoder.extract_embedding(file_path)
        
        if embedding is None:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract face embedding"
            )
            
        #Save to database
        async with AsyncSessionLocal() as db:
            #creating new face record
            new_face=Face(
                user_id=employee_user.id,
                original_image_path=file_path,
                processed_image_path=file_path,
                detection_confidence=face_info["confidence"],
                face_box=str(face_info["box"]),
                quality_score=face_info["quality_score"],
                is_blurry=face_info["is_blurry"],
                brightness_score=face_info["brightness"],
                is_primary=False
            )
            db.add(new_face)
            await db.commit()
            await db.refresh(new_face)
            
            #Creating encoding record
            new_encoding=Encoding(
                face_id=new_face.id,
                embedding=face_encoder.serialize_embedding(embedding),
                model_name=face_encoder.model_name,
                model_version="1.0"
            )
            db.add(new_encoding)
            await db.commit()
            logger.info(f"Registered face {new_face.id} for employee {employee_id} ({full_name})")
            
            # Return proper response format
            return FaceRegisterResponse(
                success=True,
                message=f"Face registered successfully for {full_name}",
                employee_id=employee_id,
                face_id=new_face.id,
                image_url=file_path
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering face: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register face: {str(e)}"
        )
    
@router.post("/match",response_model=FaceMatchResponse)
            
@router.get("/my-faces",response_model=list[FaceDetailResponse])
async def get_my_faces(
    authorization: str=Header(None)
):
    """Get all faces registreed by current user"""
    user= await get_current_user_from_token(authorization)
    
    async with AsyncSessionLocal() as db:
        result =await db.execute(
            select(Face).where(Face.user_id==user.id)
        )
        faces=result.scalars().all()
        return faces
    
    
    @router.delete("/{face_id}")
    async def delete_face(
        face_id:int,
        authorization:str=Header(None)
        
    ):
        #Deleting a face by face id
        user =await get_current_user_from_token(authorization)
        
        async with AsyncSessionLocal() as db:
            result=await db.execute(
                select(Face).where(Face.id==face_id,Face.user_id==user.id)
            )
            face=result.scalar_one_or_none()
            if not face:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Face not found"
                )
            #deleting face
            if face.original_image_path and os.path.exists(face.original_image_path):
                os.remove(face.original_image_path)
                
            await db.delete(face)
            await db.commit()
            return {"message": "Face Deleted Successfully"}


@router.post("/match-camera", response_model=FaceMatchResponse)
async def match_face_from_camera(
    file: UploadFile = File(...)
):
    """
    Match face from camera/webcam capture
    
    This endpoint accepts image captured from webcam and matches against database.
    No authentication required for quick face matching.
    """
    temp_path = None
    
    try:
        logger.info(f"Received camera capture: {file.filename}, content_type: {file.content_type}")
        
        # Save temporary file
        temp_dir = "./data/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        logger.info(f"Saving to temp path: {temp_path}")
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.info(f"Saved {len(content)} bytes")
        
        # Detect face
        logger.info("Starting face detection...")
        face_info = face_detector.detect_face(temp_path)
        
        if not face_info:
            logger.warning("No face detected in image")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in image"
            )
        
        logger.info(f"Face detected: {face_info}")
        
        # Extract embedding
        logger.info("Extracting face embedding...")
        query_embedding = face_encoder.extract_embedding(temp_path)
        
        if query_embedding is None:
            logger.error("Failed to extract embedding")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract face embedding"
            )
        
        logger.info(f"Embedding extracted, shape: {query_embedding.shape}")
        
        # Compare with all faces in database
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Encoding, Face, User)
                .join(Face, Encoding.face_id == Face.id)
                .join(User, Face.user_id == User.id)
            )
            
            all_encodings = result.all()
            logger.info(f"Comparing against {len(all_encodings)} faces in database")
            
            matches = []
            for encoding, face, user in all_encodings:
                # Deserialize embedding
                db_embedding = face_encoder.deserialize_embedding(encoding.embedding)
                
                # Calculate similarity
                similarity = face_encoder.cosine_similarity(query_embedding, db_embedding)
                
                if similarity >= 0.6:  # Threshold
                    matches.append(FaceMatchResult(
                        user_id=user.id,
                        user_email=user.email,
                        user_name=user.full_name,
                        face_id=face.id,
                        similarity=similarity,
                        quality_score=face.quality_score
                    ))
            
            # Sort by similarity
            matches.sort(key=lambda x: x.similarity, reverse=True)
            
            logger.info(f"Camera match: Found {len(matches)} matches")
            
            if len(matches) > 0:
                best = matches[0]
                # Get employee_id from User
                user_result = await db.execute(
                    select(User).where(User.id == best.user_id)
                )
                user = user_result.scalar_one_or_none()
                
                return FaceMatchResponse(
                    match_found=True,
                    employee_id=user.employee_id if user else None,
                    full_name=best.user_name,
                    confidence=best.similarity,
                    message=f"Match found with {(best.similarity * 100):.1f}% confidence"
                )
            else:
                return FaceMatchResponse(
                    match_found=False,
                    employee_id=None,
                    full_name=None,
                    confidence=None,
                    message="No matching face found in database"
                )
    
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in match-camera: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching error: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Cleaned up temp file: {temp_path}")


# ============================================
# ATTENDANCE ENDPOINTS
# ============================================

from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.attendance import (
    AttendanceMarkRequest,
    AttendanceResponse,
    AttendanceMarkResponse,
    AttendanceAnalytics
)
from datetime import date, timedelta
from sqlalchemy import func, and_, extract


@router.post("/attendance/mark", response_model=AttendanceMarkResponse)
async def mark_attendance(
    request: AttendanceMarkRequest
):
    """
    Mark attendance for an employee after successful face match.
    This endpoint is called from the live camera feed after a face is matched.
    """
    async with AsyncSessionLocal() as db:
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if attendance already marked for today
        today = date.today()
        existing_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.user_id == request.user_id,
                    Attendance.date == today
                )
            )
        )
        existing_attendance = existing_result.scalar_one_or_none()
        
        if existing_attendance:
            return AttendanceMarkResponse(
                success=False,
                message=f"Attendance already marked for {user.full_name} today at {existing_attendance.time_in.strftime('%I:%M %p')}",
                attendance=AttendanceResponse.model_validate(existing_attendance)
            )
        
        # Create new attendance record
        from datetime import datetime
        new_attendance = Attendance(
            user_id=request.user_id,
            date=today,
            time_in=datetime.now(),
            status=AttendanceStatus.PRESENT
        )
        
        db.add(new_attendance)
        await db.commit()
        await db.refresh(new_attendance)
        
        logger.info(f"Attendance marked for user {user.full_name} (ID: {user.employee_id})")
        
        return AttendanceMarkResponse(
            success=True,
            message=f"Attendance marked successfully for {user.full_name}",
            attendance=AttendanceResponse.model_validate(new_attendance)
        )


@router.get("/attendance/my-records", response_model=list[AttendanceResponse])
async def get_my_attendance_records(
    authorization: str = Header(None),
    limit: int = 30
):
    """
    Get attendance records for the logged-in employee.
    Returns the last 'limit' records (default 30 days).
    """
    user = await get_current_user_from_token(authorization)
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Attendance)
            .where(Attendance.user_id == user.id)
            .order_by(Attendance.date.desc())
            .limit(limit)
        )
        attendances = result.scalars().all()
        
        return [AttendanceResponse.model_validate(att) for att in attendances]


@router.get("/attendance/analytics", response_model=AttendanceAnalytics)
async def get_attendance_analytics(
    authorization: str = Header(None)
):
    """
    Get attendance analytics for the logged-in employee.
    Includes total days, present/absent counts, and attendance percentage.
    """
    user = await get_current_user_from_token(authorization)
    
    async with AsyncSessionLocal() as db:
        # Get all attendance records
        result = await db.execute(
            select(Attendance).where(Attendance.user_id == user.id)
        )
        all_attendances = result.scalars().all()
        
        # Calculate statistics
        total_days = len(all_attendances)
        present_days = sum(1 for att in all_attendances if att.status == AttendanceStatus.PRESENT)
        absent_days = sum(1 for att in all_attendances if att.status == AttendanceStatus.ABSENT)
        half_days = sum(1 for att in all_attendances if att.status == AttendanceStatus.HALF_DAY)
        leave_days = sum(1 for att in all_attendances if att.status == AttendanceStatus.LEAVE)
        
        # Calculate attendance percentage
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
        
        # Current month statistics
        today = date.today()
        current_month_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.user_id == user.id,
                    extract('year', Attendance.date) == today.year,
                    extract('month', Attendance.date) == today.month
                )
            )
        )
        current_month_attendances = current_month_result.scalars().all()
        current_month_total = len(current_month_attendances)
        current_month_present = sum(
            1 for att in current_month_attendances 
            if att.status == AttendanceStatus.PRESENT
        )
        
        return AttendanceAnalytics(
            total_days=total_days,
            present_days=present_days,
            absent_days=absent_days,
            half_days=half_days,
            leave_days=leave_days,
            attendance_percentage=round(attendance_percentage, 2),
            current_month_present=current_month_present,
            current_month_total=current_month_total
        )
        
        
        
from fastapi.responses import FileResponse
from openpyxl import Workbook
from datetime import datetime
import os

@router.get("/attendance/report")
async def export_attendance(
    start_date:str=None,
    end_date:str=None,
    authorization:str=Header(None)
):
    
    #verifuing admin
    current_user=await get_current_user_from_token(authorization)
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="only administrators can export attendance reports"
        )
    
    async with AsyncSessionLocal() as db:
        try:
            query=select(Attendance,User).join(
                User,Attendance.user_id==User.id
            ).order_by(Attendance.date.desc())
            
            if start_date:
                query=query.filter(Attendance.date>=start_date)
            if end_date:
                query=query.filter(Attendance.date<=end_date)
                
            #execuring query
            result=await db.execute(query)
            records=result.all()
            
            #Creating Excel workbook
            
            wb=Workbook()
            ws=wb.active
            ws.title="Attendance Report"
            
            headers= [
                "Date",
                "employee_id",
                "Employee Name",
                "Time in",
                "Time out",
                "Status",
                "Day of Week"
            ]
            ws.append(headers)
            
            #making headers bold
            for cell in ws[1]:
                cell.font=Font(bold=True)
                
            #addng data
            for attendance,user in records:
                ws.append([
                    attendance.data.strftime("%Y-%m-%d"),
                    user.employee_id,
                    user.full_name,
                    attendance.time_in.strftime("%I:%M %p") if attendance.time_in else "",
                    attendance.time_out.strftime("%I:%M %p") if attendance.time_out else "",
                    attendance.status,
                    attendance.date.strftime("%A")
                ])
                
            for column in ws.columns:
                max_length=0
                column=[cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value))> max_length:
                            max_length=len(cell.value)
                        
                    except:
                        pass
                    
                    adjusted_width = (max_length + 2)
                    ws.column_dimensions[column[0].column_letter].width = adjusted_width
                    
            #Saving the file
            temp_dir="./data/temp"
            os.makedirs(temp_dir,exist_ok=True)
            
            filename=f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath=os.path.join(temp_dir,filename)
            
            wb.save(filepath)
            
            logger.info(f"Created Attendance report: {filepath}")
            
            #returning the file
            return FileResponse(
                path=filepath,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheet.sheet",
                background=BackgroundTask(lambda: os.remove(filepath))  #cleanup
            )
        
        except Exception as e:
            logger.error(f"Export failed:{str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to export : {str(e)}"
            )
                