# app/core/config.py
try:
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover - fallback for Pydantic v1
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # SBO credentials for the auth endpoint
    API_SBO_USER: str
    API_SBO_PASS: str

    # JWT configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # General settings
    PORT: int = 1987

    # Odoo JSON-RPC
    ODOO_URL: str = "http://localhost:8069"
    ODOO_DB: str = ""
    ODOO_USER: str = ""
    ODOO_PASSWORD: str = ""

    # Jaeger
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
