# app/api/customers.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.customer import CustomerCreate, CustomerRead
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger
from fastapi import Depends
from slowapi import Limiter

router = APIRouter(
    prefix="/api/customers",
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())],
)

@router.post(
    "/",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo cliente en Odoo",
)
def create_customer(customer: CustomerCreate):
    try:
        # 1) Crear registro en Odoo
        partner_id = odoo.create("res.partner", customer.dict())
        # 2) Leer el registro recién creado para devolverlo
        partners = odoo.search_read(
            "res.partner",
            domain=[["id", "=", partner_id]],
            fields=["id", "name", "email", "phone", "company_type"],
        )
        if not partners:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cliente creado pero no se puede leer.",
            )
        # Devuelve el primer (y único) elemento
        return partners[0]
    except Exception as e:
        logger.error(f"Error creando cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Obtener datos de un cliente por ID"
)
def read_customer(customer_id: int):
    try:
        partners = odoo.search_read(
            "res.partner",
            domain=[["id", "=", customer_id]],
            fields=["id", "name", "email", "phone", "company_type"],
        )
        if not partners:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado.",
            )
        return partners[0]
    except Exception as e:
        logger.error(f"Error leyendo cliente {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
