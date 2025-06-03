# app/utils/jwt.py
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status
from app.core.config import settings

def sign_jwt(subject: str) -> str:
    """
    Genera un JWT con los claims 'sub' y 'exp'.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_jwt(token: str) -> dict:
    """
    Decodifica y verifica firma + expiración.
    Devuelve el payload si es válido o lanza HTTPException(401).
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require_sub": True, "require_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
