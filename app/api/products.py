# app/api/products.py
from fastapi import APIRouter, Query, Depends, HTTPException, Response, status
from typing import List, Optional
from datetime import datetime
from hashlib import md5

from app.models.product import Product
from app.utils.auth import JWTBearer

router = APIRouter(prefix="/api/v1", tags=["Products"], dependencies=[Depends(JWTBearer())])

# Static dataset for demonstration purposes
PRODUCTS = [
    Product(
        sku="SKU-ABC-01",
        name="Suscripción Digital 12M",
        standard_cost=9.8,
        list_price=12.5,
        uom="unid",
        category_id=7,
        updated_at=datetime(2025, 5, 24, 12, 15, 23),
        status="active",
    ),
    Product(
        sku="SKU-XYZ-99",
        name="Producto Demo",
        standard_cost=5.0,
        list_price=8.0,
        uom="unid",
        category_id=7,
        updated_at=datetime(2025, 5, 20, 8, 0, 0),
        status="inactive",
    ),
]


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
    data = PRODUCTS

    # Filtering
    if q:
        data = [p for p in data if q.lower() in p.name.lower() or q.lower() in p.sku.lower()]
    if sku:
        data = [p for p in data if p.sku == sku]
    if category_id is not None:
        data = [p for p in data if p.category_id == category_id]
    if updated_since:
        data = [p for p in data if p.updated_at >= updated_since]
    if status:
        data = [p for p in data if p.status == status]

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
    for product in PRODUCTS:
        if product.sku == sku:
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
