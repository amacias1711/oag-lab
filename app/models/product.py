from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    sku: str
    name: str
    standard_cost: float
    list_price: float
    uom: str
    category_id: int
    updated_at: datetime
    status: Optional[str] = "active"
