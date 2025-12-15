# Cấu hình logging 
# app/core/logger.py
from loguru import logger

logger.configure(handlers=[{"sink": "app.log", "level": "INFO", "rotation": "10 MB"}])

__all__ = ["logger"]
