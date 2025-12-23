from app.core.logger import logger, log_api_request, log_ml_operation

logger.debug("this is a debug message")
logger.info("this is an info")
logger.warning("this is a warning")
logger.error("this is an error")

log_api_request("POST", "/api/v1/faces/register", user_id="123", request_id="abc-def")

log_ml_operation(
    operation="face_detection",
    duration_ms=45.3,
    success=True,
    details={"faces_found": 2, "confidence": 0.95}
)


