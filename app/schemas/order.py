from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    title: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemBase]
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_postal_code: str
    payment_method: str = "online"


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    status: OrderStatus
    payment_method: str
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_postal_code: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True