from fastapi import APIRouter, Depends, HTTPException, status
from app.models.delivery import DeliveryCreate, DeliveryRead
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/entregas",
    tags=["Entregas"],
    dependencies=[Depends(JWTBearer())],
)

@router.post(
    "/",
    response_model=DeliveryRead,
    status_code=status.HTTP_200_OK,
    summary="Confirmar entrega de una orden",
)
def confirm_delivery(delivery: DeliveryCreate):
    try:
        # 1) Actualizar la orden en Odoo
        vals = {
            "carrier_tracking_ref": delivery.tracking_number,
            "state": "done",  # o el estado que corresponda
        }
        odoo.write("sale.order", [delivery.order_id], vals)

        # 2) Leer la orden para devolver estado y tracking
        rec = odoo.search_read(
            "sale.order",
            domain=[["id", "=", delivery.order_id]],
            fields=["id", "carrier_tracking_ref", "state"],
        )
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo leer la orden tras confirmación",
            )
        raw = rec[0]
        return DeliveryRead(
            order_id=raw["id"],
            tracking_number=raw.get("carrier_tracking_ref", ""),
            status=raw.get("state", ""),
        )
    except Exception as e:
        logger.error(f"Error confirmando entrega: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
