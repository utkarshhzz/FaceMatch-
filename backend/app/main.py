#Main dast api applciaton

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.logger import logger
from app.api.v1 import auth,faces

app=FastAPI(
    title="FaceMatch++ API",
    description="Advanced face recognition system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files (check if directory exists first)
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,prefix="/api/v1")
app.include_router(faces.router,prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    
#Runs when applictionsv strtsa
    logger.info("="*60)
    logger.info("Starting FaceMatch++ API ...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("="*60)
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("="*60)
    logger.info("Shutting down FaceMatch++ API ...")
    logger.info("="*60)
    
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Welcome to FaceMatch++ API",
        "version": "1.0.0"
    }
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "FaceMatch++ API is healthy",
        "version": "1.0.0"
    }