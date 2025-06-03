# app/core/config.py
import os
from dotenv import load_dotenv

# Carga variables de .env automáticamente
load_dotenv()

class Settings:
    # Odoo JSON-RPC
    ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB: str = os.getenv("ODOO_DB", "")
    ODOO_USER: str = os.getenv("ODOO_USERNAME", "")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "")

    # API Gateway
    #API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    PORT: int = int(os.getenv("PORT", "1987"))

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # SBO
    SBO_USER: str = os.getenv("SBO_USER", "sbo")
    SBO_PASSWORD: str = os.getenv("SBO_PASSWORD", "")

    # Jaeger
    JAEGER_HOST: str = os.getenv("JAEGER_HOST", "localhost")
    JAEGER_PORT: int = int(os.getenv("JAEGER_PORT", "6831"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
