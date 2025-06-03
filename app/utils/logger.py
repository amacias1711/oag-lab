# app/utils/logger.py
from loguru import logger
import sys
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Eliminar configuración por defecto y agregar nuestra propia
logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
