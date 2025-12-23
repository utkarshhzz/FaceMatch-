#Face detection and quality assessment

import cv2
import numpy as np
from typing import Optional,Dict,Tuple
from app.core.logger import logger

class FaceDetector:
    """Detects faces in image and accesses quality"""
    
    def __init__(self):
        #loading haarcascade for face detection
        cascade_path=cv2.data.haarcascades+'haarcascade_frontalface_default.xml'
        self.face_cascade= cv2.CascadeClassifier(cascade_path)
        
    def detect_face(self,image_path:str) ->Optional[Dict]:
        try:
            #read image
            img=cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image:{image_path}")
                return None
            
            #convert to grey scale for detection
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
            #Try multiple detection parameters for better results
            # First attempt with standard parameters
            faces=self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30,30)
            )
            
            # If no face found, try with more lenient parameters
            if len(faces) == 0:
                faces=self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(20,20)
                )
            
            # If still no face, try even more lenient
            if len(faces) == 0:
                faces=self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.02,
                    minNeighbors=2,
                    minSize=(15,15)
                )
            
            if len(faces)==0:
                logger.warning("No face detected")
                return None
            
            if len(faces) >1:
                logger.warning(f"Multiple faces detected:({len(faces)}), using largesr")
                
            #Seleting largest face by area
            largest_face= max(faces,key=lambda f: f[2]*f[3])
            x,y,w,h= largest_face
            
            #Extract face region
            face_roi= img[y:y+h,x:x+w]
            
            #Calculate quality metrics
            quality_metrrics= self._assess_quality(face_roi,gray[y:y+h,x:x+w])
            return {
                "box":[int(x),int(y),int(w),int(h)],
                "confidence":0.95,
                **quality_metrrics
            }
        except Exception as e:
            logger.error(f"Error detecting face: {e}")
            return None
        
    def _assess_quality(self,face_rgb:np.ndarray,face_gray:np.ndarray)-> Dict:
        laplacian_var=cv2.Laplacian(face_gray,cv2.CV_64F).var()
        is_blurry= laplacian_var <100 #threshold for blur
        
        #Brightness
        brightness=np.mean(face_gray)
        
        #Face Size
        face_size=min(face_rgb.shape[0],face_rgb.shape[1])
        
        #Overall quality Score
        quality_score= self._calculate_quality_score(
            laplacian_var,brightness,face_size
        )
        
        return {
            "quality_score": round(quality_score,2),
            "is_blurry": bool(is_blurry),
            "brightness": round(float(brightness),2),
            "face_size": int(face_size)
        }
        
    def _calculate_quality_score(
        self,
        blur_score:float,
        brightness:float,
        size:int)->float:
        blur_component=min(blur_score/200,1.0)
        
        if 80<= brightness <=200:
            brightness_component=1.0
        elif brightness <80:
            brightness_component= brightness/80
        else:
            brightness_component= max(1.0-(brightness-200)/55,0.0)
            
        size_component=min(size/150,1.0)
        
        #weighted avg
        quality=(
            0.4*blur_component+0.3*brightness_component+0.3* size_component
        )
        
        return quality
#creating singleton instance
face_detector=FaceDetector()
        