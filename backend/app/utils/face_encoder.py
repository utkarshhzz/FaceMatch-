"""Face embedding extraction using deepface"""

import numpy as np
from deepface import DeepFace
from typing import Optional
import pickle
from app.core.logger import logger

class FaceEncoder:
    """to extract face embedding usin g Arcface model"""
    def __init__(self,model_name:str="ArcFace"):
        self.model_name=model_name
        logger.info("Initialised FaceEncoder with {model_name} model")
        
    def extract_embedding(self,image_path:str)-> Optional[np.ndarray]:
        """
        Extract face embedding using DeepFace with multiple detector backends for robustness.
        Tries modern detectors that work with glasses, different lighting, etc.
        """
        # Try multiple detector backends for better robustness
        detector_backends = ['retinaface', 'mtcnn', 'ssd', 'opencv']
        
        for backend in detector_backends:
            try:
                logger.info(f"Trying embedding extraction with detector: {backend}")
                
                embedding_objs = DeepFace.represent(
                    img_path=image_path,
                    model_name=self.model_name,
                    enforce_detection=False,
                    detector_backend=backend
                )
                
                if not embedding_objs:
                    logger.debug(f"No embedding extracted with {backend}")
                    continue
                    
                # Get first embedding (in case of multiple faces)
                embedding = np.array(embedding_objs[0]["embedding"])
                
                logger.info(f"Extracted embedding of shape {embedding.shape} using {backend}")
                return embedding
                
            except Exception as e:
                logger.debug(f"Embedding extraction failed with {backend}: {str(e)}")
                continue
        
        # If all backends failed
        logger.error("Failed to extract embedding with all detector backends")
        return None
        
    @staticmethod
    def serialize_embedding(embedding: np.ndarray) -> bytes:
        #converting fom numpy array to byres
        return pickle.dumps(embedding)
    
    @staticmethod
    def deserialize_embedding(embedding_bytes:bytes) -> np.ndarray:
        #convertn=ing again from bytes tonumpy array
        return pickle.loads(embedding_bytes)
    
    @staticmethod
    def cosine_similarity(embedding1: np.ndarray,embedding2:np.ndarray) ->float:
        ###Computing cosine siilarity between the two embeddings
        #normalizing the vectors
        embedding1_norm=embedding1/np.linalg.norm(embedding1)
        embedding2_norm=embedding2/np.linalg.norm(embedding2)
        
        #Cosine similarity
        similarity=np.dot(embedding1_norm,embedding2_norm)
        
        #Converting to 0-1 range
        similarity=(similarity+1)/2
        return float(similarity)
    
#crating singleton instance
face_encoder=FaceEncoder()