"""
Logging configuration
"""
import os
from loguru import logger


def setup_logger(log_level: str = "INFO", log_file: str = "logs/crawler.log") -> None:
    """
    Setup logging configuration
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file path
    """
    logger.remove()
    
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
    )
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=log_level,
        rotation="500 MB",
        retention="7 days",
    )
    
    logger.info(f"Logger initialized with level {log_level}")
