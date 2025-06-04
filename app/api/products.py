# app/api/products.py
from fastapi import APIRouter, Query, Depends, HTTPException, Response, status
from typing import List, Optional
from datetime import datetime
from hashlib import md5

from app.models.product import Product
from app.utils.auth import JWTBearer
from app.utils.odoo_connector import OdooConnector

router = APIRouter(prefix="/api/v1", tags=["Products"], dependencies=[Depends(JWTBearer())])

# Helper to map Odoo records to the API Product model
def _map_odoo_product(record: dict) -> Product:
    # Si default_code es False o None, lo convertimos en cadena vacía:
    sku_value = record.get("default_code") or ""
    # Si name viene como False (aunque rara vez, en general name siempre existe),
    # lo convertimos en cadena vacía:
    name_value = record.get("name") or ""
    # Para los campos numéricos o listas, igual aplicar una conversión segura:
    standard_cost_value = record.get("standard_price") or 0.0
    list_price_value     = record.get("lst_price") or 0.0

    # El uom_id viene en Odoo como [id, "Nombre de unidad"] o como False si no está.
    # Pongamos que tu modelo espera un string. Entonces:
    uom_value = ""
    if record.get("uom_id"):
        # Odoo devuelve [id, "Unidad"], por lo que tomamos el nombre (posición 1) o
        # si tu modelo en Pydantic acepta directamente el ID numérico, cambialo a record["uom_id"][0].
        uom_value = record["uom_id"][1]   # nombre de la unidad

    # Lo mismo con categ_id; mágicamente Odoo regresa [id, "Nombre categoría"] o False.
    category_value = None
    if record.get("categ_id"):
        category_value = record["categ_id"][0]  # si tu modelo quiere solo el ID
        # o bien record["categ_id"][1] si quieres poner el nombre

    # Para write_date, a veces Odoo devuelve False o None si no se ha modificado.
    updated_at_value = record.get("write_date") or datetime.utcnow()

    status_value = "active" if record.get("active") else "inactive"

    return Product(
        sku=sku_value,
        name=name_value,
        standard_cost=standard_cost_value,
        list_price=list_price_value,
        uom=uom_value,
        category_id=category_value,
        updated_at=updated_at_value,
        status=status_value,
    )


@router.get("/products", response_model=dict)
def list_products(
    response: Response,
    q: Optional[str] = Query(None, description="Texto de búsqueda"),
    sku: Optional[str] = None,
    category_id: Optional[int] = None,
    updated_since: Optional[datetime] = None,
    status: Optional[str] = None,
    page_size: int = Query(50, alias="page[size]", ge=1, le=200),
    page_number: int = Query(1, alias="page[number]", ge=1),
    sort: Optional[str] = None,
    fields: Optional[str] = None,
    include: Optional[str] = None,  # Not used but kept for spec completeness
):
    connector = OdooConnector()

    # Build Odoo domain with the provided filters
    domain: List = []
    if q:
        # Filter by name or SKU using ilike (case-insensitive)
        domain.extend(["|", ("name", "ilike", q), ("default_code", "ilike", q)])
    if sku:
        domain.append(("default_code", "=", sku))
    if category_id is not None:
        domain.append(("categ_id", "=", category_id))
    if updated_since:
        domain.append(("write_date", ">=", updated_since.strftime("%Y-%m-%d %H:%M:%S")))
    if status:
        domain.append(("active", "=", status == "active"))

    # Obtain products from Odoo using the connector
    # The connector returns raw dictionaries from odoorpc; we convert them
    records = connector.search_products(domain=domain)
    data = [_map_odoo_product(r) for r in records]

    total = len(data)

    # Sorting
    if sort:
        for key in reversed(sort.split(',')):
            if key.startswith('-'):
                field = key[1:]
                data.sort(key=lambda x: getattr(x, field), reverse=True)
            else:
                field = key.lstrip('+')
                data.sort(key=lambda x: getattr(x, field))

    # Pagination
    start = (page_number - 1) * page_size
    end = start + page_size
    paginated = data[start:end]

    # Fields selection
    def serialize(product: Product):
        d = product.dict()
        if fields:
            allowed = set(f.strip() for f in fields.split(','))
            d = {k: v for k, v in d.items() if k in allowed}
        d['_links'] = {"self": f"/api/v1/products/{product.sku}"}
        return d

    items = [serialize(p) for p in paginated]

    meta = {"total": total, "page": {"number": page_number, "size": page_size}}
    links = {
        "self": f"/api/v1/products?page[number]={page_number}&page[size]={page_size}",
    }
    if end < total:
        links["next"] = f"/api/v1/products?page[number]={page_number + 1}&page[size]={page_size}"
    if start > 0:
        links["prev"] = f"/api/v1/products?page[number]={page_number - 1}&page[size]={page_size}"

    body = {"meta": meta, "links": links, "data": items}

    # ETag and Last-Modified headers
    etag = md5(str(body).encode()).hexdigest()
    last_modified = max(p.updated_at for p in data).strftime('%a, %d %b %Y %H:%M:%S GMT') if data else None
    response.headers['ETag'] = etag
    if last_modified:
        response.headers['Last-Modified'] = last_modified
    response.headers['Cache-Control'] = 'max-age=60, public'

    return body


@router.get("/products/{sku}", response_model=Product)
def get_product(sku: str):
    connector = OdooConnector()
    record = connector.get_product_by_sku(sku)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    # Convert Odoo dict to Product model
    return _map_odoo_product(record)
