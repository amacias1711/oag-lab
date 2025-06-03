# app/api/invoices.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.invoice import InvoiceCreate, InvoiceRead, InvoiceLine
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/invoices",
    tags=["Facturación"],
    dependencies=[Depends(JWTBearer())],
)

def _build_invoice_lines(lines: List[InvoiceLine]) -> list:
    """
    Convierte la lista de InvoiceLine a comandos ORM de Odoo:
    [(0, 0, { ... }), ...]
    """
    odoo_lines = []
    for line in lines:
        odoo_lines.append((0, 0, {
            "product_id": line.product_id,
            "quantity": line.quantity,
            "price_unit": line.price_unit,
        }))
    return odoo_lines

@router.post(
    "/customers",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir factura electrónica a cliente",
)
def create_customer_invoice(invoice: InvoiceCreate):
    try:
        # Construir vals para Odoo: acto de facturación 'out_invoice'
        vals = {
            "move_type": "out_invoice",
            "partner_id": invoice.partner_id,
            "invoice_date": invoice.invoice_date,
            "invoice_line_ids": _build_invoice_lines(invoice.invoice_lines),
        }
        move_id = odoo.create("account.move", vals)

        # Leer la factura creada
        records = odoo.search_read(
            model="account.move",
            domain=[["id", "=", move_id]],
            fields=["id", "partner_id", "amount_total", "invoice_date"],
        )
        if not records:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Factura creada pero no se puede leer."
            )
        raw = records[0]
        return InvoiceRead(
            id=raw["id"],
            partner_id=raw["partner_id"][0] if isinstance(raw["partner_id"], list) else raw["partner_id"],
            amount_total=raw["amount_total"],
            invoice_date=raw["invoice_date"],
        )
    except Exception as e:
        logger.error(f"Error creando factura a cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post(
    "/suppliers",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar factura de proveedor",
)
def create_supplier_invoice(invoice: InvoiceCreate):
    try:
        # Construir vals para factura de proveedor 'in_invoice'
        vals = {
            "move_type": "in_invoice",
            "partner_id": invoice.partner_id,
            "invoice_date": invoice.invoice_date,
            "invoice_line_ids": _build_invoice_lines(invoice.invoice_lines),
        }
        move_id = odoo.create("account.move", vals)

        # Leer la factura de proveedor creada
        records = odoo.search_read(
            model="account.move",
            domain=[["id", "=", move_id]],
            fields=["id", "partner_id", "amount_total", "invoice_date"],
        )
        if not records:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Factura de proveedor creada pero no se puede leer."
            )
        raw = records[0]
        return InvoiceRead(
            id=raw["id"],
            partner_id=raw["partner_id"][0] if isinstance(raw["partner_id"], list) else raw["partner_id"],
            amount_total=raw["amount_total"],
            invoice_date=raw["invoice_date"],
        )
    except Exception as e:
        logger.error(f"Error creando factura de proveedor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
