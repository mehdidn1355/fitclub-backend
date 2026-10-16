from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    price: float
    stock: int = 0
    icon: str = "📦"
    tag: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    rating: float

    class Config:
        from_attributes = True