from pydantic import BaseModel, Field

class DeliveryCreate(BaseModel):
    order_id: int = Field(..., example=1001)
    carrier: str = Field(..., example="FedEx")
    tracking_number: str = Field(..., example="1Z9999W99999999999")

class DeliveryRead(BaseModel):
    order_id: int
    tracking_number: str
    status: str

    class Config:
        orm_mode = True
