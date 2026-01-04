### Fae recongnition endpoints

from fastapi import APIRouter,UploadFile,File,Header,HTTPException,status,Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from typing import Optional

from app.schemas.face import (
    FaceDetailResponse,
    FaceUploadResponse,
    FaceMatchResponse,
    FaceMatchResult
)

from app.models.user import User
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
    
@router.post("/register",response_model=FaceUploadResponse)
async def register_face(
    file:UploadFile=File(...),
    authorization:str=Header(None)
):
    """Uplaod and registe a face image
    1)pehle uplaoded image save karenge
    2)face detect karenge and quality cehck karenge
    3)embedding extract karenge
    4)database me save karenge
    """
    
    #Get current user
    user=await get_current_user_from_token(authorization)
    #validation
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
        
    #creating uplaod directory
    
    upload_dir=f"./data/uploads/{user.id}"
    os.makedirs(upload_dir,exist_ok=True)
    
    #generatig unique filename
    file_extension=file.filename.split(".")[-1]
    unique_filename=f"{uuid.uuid4()}.{file_extension}"
    file_path=os.path.join(upload_dir,unique_filename)
    
    #save the file at the lcoation
    with open(file_path,'wb') as f:
        content=await file.read()
        f.write(content)
        
    logger.info(f"Saved uploaded image to {file_path}")
    
    
    #FAce detection and wuality check
    face_info=face_detector.detect_face(file_path)
    if not face_info:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face detected in the image"
        )
    #CHecking quality
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
        
    #Saveto dataabase
    async with AsyncSessionLocal() as db:
        #creating new face record
        new_face=Face(
            user_id=user.id,
            original_image_path=file_path,
            processed_image_path=file_path,
            detection_confidence=face_info["confidence"],
            face_box=str(face_info["box"]),
            quality_score=face_info["quality_score"],
            is_blurry=face_info["is_blurry"],
            brightness_score=face_info["brightness"],
            is_primary=False  #user khudse baad me set kar sakta haiu
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
        logger.info(f"Regitered face {new_face.id} for usder {user.email}")
        return new_face
    
@router.post("/match",response_model=FaceMatchResponse)
async def match_face(file: UploadFile=File(...)):
    """Matching uplaoded face against daatbase"""
    #saving temp file
    temp_dir="./data/temp"
    os.makedirs(temp_dir,exist_ok=True)
    
    temp_filename=f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    temp_path=os.path.join(temp_dir,temp_filename)
    with open(temp_path,'wb') as f:
        content=await file.read()
        f.write(content)
        
    try:
        #detect face
        face_info=face_detector.detect_face(temp_path)
        if not face_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
        #Extract embedding
        query_embedding=face_encoder.extract_embedding(temp_path)
        
        if query_embedding is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract face embedding"
            )
            
        async with AsyncSessionLocal() as db:
            result= await db.execute(select(Encoding,Face,User)
                                     .join(Face,Encoding.face_id==Face.id)
                                     .join(User,Face.user_id==User.id))
            
            all_encodings=result.all()
            
            matches=[]
            for encoding,face,user in all_encodings:
                #deserialise embeddings
                db_embedding=face_encoder.deserialize_embedding(encoding.embedding)
                
                #Calculate similarity
                similarity=face_encoder.cosine_similarity(query_embedding,db_embedding)
                
                if similarity >=0.6:
                    matches.append(FaceMatchResult(
                        user_id=user.id,
                        user_email=user.email,
                        user_name=user.full_name,
                        face_id=face.id,
                        similarity=similarity,
                        quality_score=face.quality_score
                        
                    ))
                #Soritng
                matches.sort(key=lambda x:x.similarity,reverse=True)
                
                return FaceMatchResponse(
                    matched=len(matches) >0,
                    best_match=matches[0] if matches else None,
                    all_matches=matches,
                    threshold=0.6
                )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
            
            
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
    
    # Save temporary file
    temp_dir = "./data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Detect face
        face_info = face_detector.detect_face(temp_path)
        
        if not face_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in image"
            )
        
        # Extract embedding
        query_embedding = face_encoder.extract_embedding(temp_path)
        
        if query_embedding is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract face embedding"
            )
        
        # Compare with all faces in database
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Encoding, Face, User)
                .join(Face, Encoding.face_id == Face.id)
                .join(User, Face.user_id == User.id)
            )
            
            all_encodings = result.all()
            
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
            
            return FaceMatchResponse(
                matched=len(matches) > 0,
                best_match=matches[0] if matches else None,
                all_matches=matches,
                threshold=0.6
            )
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)