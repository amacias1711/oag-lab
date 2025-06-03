# app/models/order.py
from pydantic import BaseModel, Field
from typing import List

class OrderLine(BaseModel):
    product_id: int = Field(..., example=45)
    quantity: float = Field(..., example=2)
    price_unit: float = Field(..., example=25.5)

class OrderCreate(BaseModel):
    partner_id: int = Field(..., example=12)
    order_lines: List[OrderLine]

class OrderRead(BaseModel):
    id: int = Field(..., example=1001)
    partner_id: int = Field(..., example=12)
    amount_total: float = Field(..., example=51.0)
    order_lines: List[OrderLine]

    class Config:
        orm_mode = True
