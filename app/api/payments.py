from fastapi import APIRouter, Depends, HTTPException, status
from app.models.payment import PaymentCreate, PaymentRead
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/pagos",
    tags=["Pagos"],
    dependencies=[Depends(JWTBearer())],
)

@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar y validar pago de factura",
)
def confirm_payment(payment: PaymentCreate):
    try:
        # 1) Leer invoice para obtener partner_id
        inv = odoo.search_read(
            "account.move",
            domain=[["id", "=", payment.invoice_id]],
            fields=["partner_id"],
        )
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada",
            )
        partner = inv[0]["partner_id"]
        partner_id = partner[0] if isinstance(partner, list) else partner

        # 2) Crear el pago
        vals = {
            "move_type": "entry",          # tipo genérico o 'entry'
            "payment_type": "inbound",     # cobro de cliente
            "partner_id": partner_id,
            "amount": payment.amount,
            "journal_id": payment.journal_id,
            "payment_date": payment.payment_date.isoformat(),
            "invoice_ids": [(4, payment.invoice_id)],
        }
        pay_id = odoo.create("account.payment", vals)

        # 3) Validar (post) el pago si corresponde
        try:
            odoo.execute("account.payment", "action_post", [pay_id])
        except Exception:
            # Algunas versiones no requieren post()
            pass

        # 4) Leer el pago para respuesta
        rec = odoo.search_read(
            "account.payment",
            domain=[["id", "=", pay_id]],
            fields=["id", "invoice_ids", "amount", "payment_date"],
        )
        raw = rec[0]
        return PaymentRead(
            id=raw["id"],
            invoice_id=payment.invoice_id,
            amount=raw["amount"],
            payment_date=raw["payment_date"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirmando pago: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
