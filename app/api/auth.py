# app/api/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
import jwt

from app.core.config import settings
from app.utils.logger import logger
from app.utils.jwt import sign_jwt         # <— nuevo import

router = APIRouter(tags=["Auth"])

def authenticate_user(username: str, password: str) -> bool:
    """
    Solo acepta las credenciales del middleware SBO definidas en .env.
    """
    return (
        username == settings.API_SBO_USER
        and password == settings.API_SBO_PASS
    )

@router.post(
    "/api/token",
    summary="Obtener JWT",
    description="Emite un token para el middleware SBO usando credenciales de .env",
)
def login(form: OAuth2PasswordRequestForm = Depends()):
    # 1) Validación de credenciales del SBO
    if not authenticate_user(form.username, form.password):
        logger.warning(f"Login fallido para usuario={form.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    # 2) Generar y firmar el JWT
    token = sign_jwt(form.username)

    # 3) Loguear emisión exitosa
    logger.info(f"Token emitido para usuario={form.username}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }
