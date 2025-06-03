# app/api/products.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models.product import ProductBase, ProductRead
from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/products",
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())],
)

@router.get(
    "/",
    response_model=List[ProductRead],
    summary="Listar productos",
)
def list_products(
    limit: Optional[int] = Query(10, gt=0, le=100, description="Número máximo de registros"),
    offset: Optional[int] = Query(0, ge=0, description="Desplazamiento inicial"),
):
    try:
        records = odoo.search_read(
            model="product.product",
            domain=[],
            fields=["id", "name", "default_code", "list_price"],
            offset=offset,
            limit=limit,
        )
        return records
    except Exception as e:
        logger.error(f"Error listando productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener productos",
        )

@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
)
def create_product(product: ProductBase):
    try:
        vals = product.dict()
        product_id = odoo.create("product.product", vals)
        records = odoo.search_read(
            model="product.product",
            domain=[["id", "=", product_id]],
            fields=["id", "name", "default_code", "list_price"],
        )
        if not records:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Producto creado pero no se puede leer",
            )
        return records[0]
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
