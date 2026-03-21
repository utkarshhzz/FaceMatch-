from datetime import datetime,timezone
from fastapi import APIRouter

from app.core.config import settings
router=APIRouter()

@router.get("/",summary="Health Check")
async def health_check() -> dict[str,str]:
    return {
        "status":"ok",
        "service":settings.APP_NAME,
        "environment":settings.APP_ENV,
        "timestamp":datetime.now(timezone.utc).isoformat(),
    }
