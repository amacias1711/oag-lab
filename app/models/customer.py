# app/models/customer.py
from pydantic import BaseModel, EmailStr, Field

class CustomerBase(BaseModel):
    name: str = Field(..., example="Juan Pérez")
    email: EmailStr = Field(..., example="juan@correo.com")
    phone: str | None = Field(None, example="0999999999")
    company_type: str = Field("person", example="person")

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    id: int = Field(..., example=12)

    class Config:
        orm_mode = True
