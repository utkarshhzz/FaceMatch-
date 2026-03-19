import sys
from loguru import logger

def setup_logging()->None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        enqueue=True,
        backtrace=False,
        diagnose=False
    )
    
app_logger=logger