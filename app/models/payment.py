from datetime import date
from pydantic import BaseModel, Field

class PaymentCreate(BaseModel):
    invoice_id: int = Field(..., example=5001)
    amount: float = Field(..., example=51.0)
    payment_date: date = Field(default_factory=date.today)
    journal_id: int = Field(..., example=1)

class PaymentRead(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_date: date

    class Config:
        orm_mode = True
