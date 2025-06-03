# app/models/invoice.py
from pydantic import BaseModel, Field
from typing import List

class InvoiceLine(BaseModel):
    product_id: int = Field(..., example=45)
    quantity: float = Field(..., example=2)
    price_unit: float = Field(..., example=25.5)

class InvoiceCreate(BaseModel):
    partner_id: int = Field(..., example=12)
    invoice_lines: List[InvoiceLine]
    invoice_date: str | None = Field(None, example="2025-05-20")

class InvoiceRead(BaseModel):
    id: int = Field(..., example=5001)
    partner_id: int = Field(..., example=12)
    amount_total: float = Field(..., example=51.0)
    invoice_date: str = Field(..., example="2025-05-20")

    class Config:
        orm_mode = True
