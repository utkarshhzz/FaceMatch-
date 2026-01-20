import redis
import json
import numpy as np
from typing import List,Optional,Dict
import os

from sqlalchemy import values
from app.core.logger import logger

class RedisCacheService:
    def __init__(self):
        #fetting redis settings from env
        redis_host=os.getenv("REDIS_HOST","localhost")
        redis_port=int(os.getenv("REDIS_PORT",6379))
        redis_db=int(os.getenv("REDIS_DB",0))
        
        #Creating connection
        try:
            self.redis_client=redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            
            #testing connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client=None
            
    def is_available(self) -> bool:
        # checks if redis working fine
        return self.redis_client is not None
    
    def set_embedding(
        self,
        employee_id:str,
        embedding:np.ndarray,
        expire_seconds:int=3600
    ) -> bool:
        
        if not self.is_available():
            return False
        
        try:
            key=f"face:embedding:{employee_id}"
            embedding_list=embedding.tolist()
            embedding_json=json.dumps(embedding_list)
            
            # Store in redis with expiration
            self.redis_client.setex(
                name=key,
                time=expire_seconds,
                value=embedding_json
            )
            logger.info(f"Cached embedding for employee {employee_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to cache embedding for {employee_id}: {e}")
            return False
        
    def get_embedding(self,employee_id:str) -> Optional[np.ndarray]:
        if not self.is_available():
            return None
        
        try:
            key=f"face:embedding:{employee_id}"
            
            embedding_json=self.redis_client.get(key)
            
            if embedding_json is None:
                logger.info(f"Cache miss for employee {employee_id}")
                return None
            
            #Found convert back to numpy array
            embedding_list=json.loads(embedding_json)
            embedding=np.array(embedding_list)
            
            logger.info(f"Cache hit for employee {employee_id}")
            return embedding
        
        except Exception as e:
            logger.error(f"Failed to retrieve embedding for {employee_id}: {e}")
            return None
        
        
    def set_all_embeddings(
        self,
        embeddings: Dict[str,np.ndarray],
        expire_seconds: int=3600
    ) -> bool:
        # store multiple embeddings at once
        
        if not self.is_available():
            return False
        
        try:
            pipe=self.redis_client.pipeline()
            for employee_id,embedding in embeddings.items():
                key=f"face:embedding:{employee_id}"
                embedding_list=embedding.tolist()
                embedding_json=json.dumps(embedding_list)
                
                pipe.setex(
                    key,
                    expire_seconds,
                    embedding_json
                )
                pipe.execute()
                
                logger.info(f"Cached {len(embeddings)} embeddings in batch ")
                return True
            
        except Exception as e:
            logger.error(f"Failed to cache embeddings in batch: {e}")
            return False
        
        
    def get_all_embeddings(self) -> Dict[str,np.ndarray]:
        if not self.is_available():
            return {}
        
        try:
            #finding all embeddings keys
            pattern="face:embedding:*"
            keys=self.redis_client.keys(pattern)
            
            if not keys:
                logger.info("No embeddings found in cache")
                return {}
            
            values = self.redis_client.mget(keys)
            
            embeddings={}
            for key,value in zip(keys,values):
                if value:
                    employee_id=key.split(":")[-1]
                    
                    embedding_list=json.loads(value)
                    embedding=np.array(embedding_list)
                    embeddings[employee_id]=embedding
                    
            logger.info(f"Retrieved {len(embeddings)} embeddings from cache")
            return embeddings
        
        except Exception as e:
            logger.error(f"Failed to retrieve embeddings from cache: {e}")
            return {}
        
        
    def delete_embedding(self,employee_id:str)-> bool:
        if not self.is_available():
            return False
        
        try:
            key=f"face:embedding:{employee_id}"
            result=self.redis_client.delete(key)
            
            if result:
                logger.info(f"Deleted cache for employee {employee_id}")
                return True
            
            else:
                logger.info(f"Embedding not found in cache for employee {employee_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete embedding for {employee_id}: {e}")
            return False    
        
        
    def clear_all(self) -> bool:
        # delete all cached embeddings
            
        if not self.is_available():
            return False
        
        try:
            #Finding all embeddings
            pattern="face:embedding:*"
            keys=self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared all embeddings from cache")
            else:
                logger.info("No embeddings to clear from cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear embeddings from cache: {e}")
            return False
        
        
redis_cache=RedisCacheService()