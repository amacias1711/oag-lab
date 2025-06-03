from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.odoo_connector import odoo
from app.utils.auth import JWTBearer
from app.utils.logger import logger
from app.models.product_v1 import ProductList, ProductItem, ProductSingle

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())],
)

# Helper to parse sort string to Odoo order clause

def _parse_sort(sort: Optional[str]) -> Optional[str]:
    if not sort:
        return None
    parts = []
    for item in sort.split(','):
        item = item.strip()
        if not item:
            continue
        direction = 'asc'
        if item.startswith('-'):
            direction = 'desc'
            item = item[1:]
        elif item.startswith('+'):
            item = item[1:]
        parts.append(f"{item} {direction}")
    return ', '.join(parts) if parts else None


def _map_product(rec: dict) -> dict:
    return {
        "sku": rec.get("default_code"),
        "name": rec.get("name"),
        "standard_cost": rec.get("standard_price"),
        "list_price": rec.get("list_price"),
        "uom": rec.get("uom_id")[1] if isinstance(rec.get("uom_id"), list) else rec.get("uom_id"),
        "category_id": rec.get("categ_id")[0] if isinstance(rec.get("categ_id"), list) else rec.get("categ_id"),
        "updated_at": rec.get("write_date"),
        "_links": {"self": f"/api/v1/products/{rec.get('default_code')}"},
    }


@router.get("/", summary="Listar productos", response_model=ProductList)
def list_products(
    q: Optional[str] = Query(None, description="Búsqueda por texto"),
    sku: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    updated_since: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None, regex="^(active|inactive)$"),
    page_size: int = Query(50, alias="page[size]", gt=0, le=200),
    page_number: int = Query(1, alias="page[number]", ge=1),
    sort: Optional[str] = Query(None),
    fields: Optional[str] = Query(None),
    include: Optional[str] = Query(None),
):
    try:
        domain = []
        if sku:
            domain.append(["default_code", "=", sku])
        if category_id:
            domain.append(["categ_id", "=", category_id])
        if updated_since:
            domain.append(["write_date", ">=", updated_since.isoformat()])
        if status:
            domain.append(["active", "=", True if status == "active" else False])
        if q:
            domain.append(["name", "ilike", q])

        total_ids = odoo.search("product.product", domain)
        total = len(total_ids)

        offset = (page_number - 1) * page_size

        order = _parse_sort(sort)
        fields_list = fields.split(',') if fields else [
            "default_code", "name", "standard_price", "list_price",
            "uom_id", "categ_id", "write_date"
        ]

        records = odoo.search_read(
            model="product.product",
            domain=domain,
            fields=fields_list,
            offset=offset,
            limit=page_size,
            order=order,
        )

        data = [_map_product(r) for r in records]

        links = {
            "self": f"/api/v1/products?page[number]={page_number}&page[size]={page_size}"
        }
        if offset + page_size < total:
            links["next"] = f"/api/v1/products?page[number]={page_number + 1}&page[size]={page_size}"
        if page_number > 1:
            links["prev"] = f"/api/v1/products?page[number]={page_number - 1}&page[size]={page_size}"

        return {
            "meta": {"total": total, "page": {"number": page_number, "size": page_size}},
            "links": links,
            "data": data,
        }
    except Exception as e:
        logger.error(f"Error listando productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener productos",
        )


@router.get("/{sku}", summary="Obtener un producto por SKU", response_model=ProductItem)
def read_product(sku: str):
    try:
        records = odoo.search_read(
            model="product.product",
            domain=[["default_code", "=", sku]],
            fields=[
                "default_code",
                "name",
                "standard_price",
                "list_price",
                "uom_id",
                "categ_id",
                "write_date",
            ],
            limit=1,
        )
        if not records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return _map_product(records[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leyendo producto {sku}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener producto")
