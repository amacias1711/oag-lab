# app/api/health.py
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get(
    "/api/health",
    summary="Health check básico",
    response_model=dict,
)
def health():
    return {"status": "ok"}
