#Face detection and quality assessment

import cv2
import numpy as np
from typing import Optional,Dict,Tuple
from app.core.logger import logger
from deepface import DeepFace

class FaceDetector:
    """Detects faces in image and accesses quality using modern deep learning models"""
    
    def __init__(self):
        # Use multiple detector backends for robustness
        # Priority: retinaface (best) -> mtcnn -> ssd -> opencv (fallback)
        self.detector_backends = ['retinaface', 'mtcnn', 'ssd', 'opencv']
        logger.info(f"Initialized FaceDetector with backends: {self.detector_backends}")
        
    def detect_face(self,image_path:str) ->Optional[Dict]:
        """
        Detect face using DeepFace with multiple backend detectors.
        Tries modern detectors first (RetinaFace, MTCNN) then falls back to simpler ones.
        """
        try:
            #read image
            img=cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image:{image_path}")
                return None
            
            # Try each detector backend until one succeeds
            for backend in self.detector_backends:
                try:
                    logger.info(f"Trying face detection with backend: {backend}")
                    
                    # Use DeepFace to detect and extract face
                    face_objs = DeepFace.extract_faces(
                        img_path=image_path,
                        detector_backend=backend,
                        enforce_detection=False,
                        align=True
                    )
                    
                    if not face_objs or len(face_objs) == 0:
                        logger.debug(f"No face detected with {backend}")
                        continue
                    
                    # Get the face with highest confidence
                    best_face = max(face_objs, key=lambda x: x.get('confidence', 0))
                    
                    # Check if confidence is reasonable (even with enforce_detection=False)
                    confidence = best_face.get('confidence', 0)
                    if confidence < 0.5:
                        logger.debug(f"Low confidence ({confidence}) with {backend}")
                        continue
                    
                    facial_area = best_face['facial_area']
                    x = facial_area['x']
                    y = facial_area['y']
                    w = facial_area['w']
                    h = facial_area['h']
                    
                    logger.info(f"Face detected successfully with {backend}! Confidence: {confidence:.2f}, Box: ({x},{y},{w},{h})")
                    
                    # Extract face region for quality assessment
                    face_roi = img[y:y+h, x:x+w]
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    face_gray = gray[y:y+h, x:x+w]
                    
                    # Calculate quality metrics
                    quality_metrics = self._assess_quality(face_roi, face_gray)
                    
                    return {
                        "box": [int(x), int(y), int(w), int(h)],
                        "confidence": float(confidence),
                        "detector": backend,
                        **quality_metrics
                    }
                    
                except Exception as e:
                    logger.debug(f"Backend {backend} failed: {str(e)}")
                    continue
            
            # If all backends failed
            logger.warning(f"No face detected with any backend. Image size: {img.shape}")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting face: {e}", exc_info=True)
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
        