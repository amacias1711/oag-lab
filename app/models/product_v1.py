from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ProductItem(BaseModel):
    sku: str = Field(..., example="SKU-ABC-01")
    name: str = Field(..., example="Suscripción Digital 12M")
    standard_cost: Optional[float] = Field(None, example=9.8)
    list_price: Optional[float] = Field(None, example=12.5)
    uom: Optional[str] = Field(None, example="unid")
    category_id: Optional[int] = Field(None, example=7)
    updated_at: Optional[datetime] = Field(None, example="2025-05-24T12:15:23Z")
    _links: Optional[dict] = None

class PageInfo(BaseModel):
    number: int
    size: int

class Meta(BaseModel):
    total: int
    page: PageInfo

class Links(BaseModel):
    self: str
    next: Optional[str] = None
    prev: Optional[str] = None

class ProductList(BaseModel):
    meta: Meta
    links: Links
    data: List[ProductItem]

class ProductSingle(BaseModel):
    data: ProductItem
    links: Links | None = None
