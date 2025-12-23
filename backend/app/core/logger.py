#Custom made professional logger for Facemach

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime
import traceback

from app.core.config import settings


#Custom json formatter
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        log_record['level'] = record.levelname
        log_record['logger_name'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line_number'] = record.lineno
        log_record['environment'] = settings.ENVIRONMENT
        
        if record.exc_info:
            log_record['exception'] = traceback.format_exception(*record.exc_info)


#Setup logger function
def setup_logger(name="facematch"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    if logger.handlers:
        return logger
    
    #HANDLER 1: Console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    console_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    #HANDLER 2: File output
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(
        filename=settings.LOG_FILE,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(message)s %(logger_name)s'
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    logger.propagate = False
    return logger


#Global logger instance
logger = setup_logger()


#Helper functions
def log_api_request(method, path, user_id=None, request_id=None):
    logger.info(
        "API Request",
        extra={
            "method": method,
            "path": path,
            "user_id": user_id,
            "request_id": request_id
        }
    )


def log_api_response(method, path, status_code, duration_ms, request_id=None):
    logger.info(
        "API Response",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "request_id": request_id
        }
    )


def log_ml_operation(operation, duration_ms, success, details=None):
    log_data = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "success": success
    }
    
    if details:
        log_data.update(details)
    
    if success:
        logger.info(f"ML Operation: {operation}", extra=log_data)
    else:
        logger.error(f"ML Operation Failed: {operation}", extra=log_data)

        