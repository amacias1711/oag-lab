# app/api/orders.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.order import OrderCreate, OrderRead, OrderLine
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/orders",
    tags=["Órdenes"],
    dependencies=[Depends(JWTBearer())],
)

@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una orden de venta en Odoo",
)
def create_order(order: OrderCreate):
    try:
        # Transformar líneas Pydantic a formato Odoo
        odoo_lines = []
        for line in order.order_lines:
            odoo_lines.append((0, 0, {
                "product_id": line.product_id,
                "product_uom_qty": line.quantity,
                "price_unit": line.price_unit,
            }))
        vals = {
            "partner_id": order.partner_id,
            "order_line": odoo_lines,
        }
        # Crear la orden
        order_id = odoo.create("sale.order", vals)

        # Leer la orden para la respuesta
        # Primero leemos los campos básicos de sale.order
        orders = odoo.search_read(
            model="sale.order",
            domain=[["id", "=", order_id]],
            fields=["id", "partner_id", "amount_total"],
        )
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Orden creada pero no se puede leer."
            )
        raw = orders[0]

        # Luego leemos las líneas asociadas
        line_ids = raw.get("order_line", [])
        lines = odoo.search_read(
            model="sale.order.line",
            domain=[["id", "in", line_ids]],
            fields=["product_id", "product_uom_qty", "price_unit"],
        )
        # Mapear al esquema OrderLine
        order_lines = [
            OrderLine(
                product_id=ln["product_id"][0] if isinstance(ln["product_id"], list) else ln["product_id"],
                quantity=ln["product_uom_qty"],
                price_unit=ln["price_unit"],
            ) for ln in lines
        ]

        return OrderRead(
            id=raw["id"],
            partner_id=raw["partner_id"][0] if isinstance(raw["partner_id"], list) else raw["partner_id"],
            amount_total=raw["amount_total"],
            order_lines=order_lines,
        )

    except Exception as e:
        logger.error(f"Error creando orden de venta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Obtener una orden de venta por ID",
)
def read_order(order_id: int):
    try:
        # Leer datos de la orden principal
        orders = odoo.search_read(
            model="sale.order",
            domain=[["id", "=", order_id]],
            fields=["id", "partner_id", "amount_total", "order_line"],
        )
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada."
            )
        raw = orders[0]

        # Leer líneas
        line_ids = raw.get("order_line", [])
        lines = odoo.search_read(
            model="sale.order.line",
            domain=[["id", "in", line_ids]],
            fields=["product_id", "product_uom_qty", "price_unit"],
        )
        order_lines = [
            OrderLine(
                product_id=ln["product_id"][0] if isinstance(ln["product_id"], list) else ln["product_id"],
                quantity=ln["product_uom_qty"],
                price_unit=ln["price_unit"],
            ) for ln in lines
        ]

        return OrderRead(
            id=raw["id"],
            partner_id=raw["partner_id"][0] if isinstance(raw["partner_id"], list) else raw["partner_id"],
            amount_total=raw["amount_total"],
            order_lines=order_lines,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leyendo orden {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
