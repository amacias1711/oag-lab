# app/models/product.py
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., example="Camisa Deportiva")
    default_code: str | None = Field(None, example="CAM-001")
    list_price: float = Field(..., example=25.5)

class ProductRead(ProductBase):
    id: int = Field(..., example=45)

    class Config:
        orm_mode = True
