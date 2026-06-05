from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    price: float
    image: str
    description: Optional[str] = None
    category: str
    stock: int
    old_price: Optional[float] = None
    rating: Optional[float] = 0.0
    orders_count: Optional[int] = 0
    free_shipping: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True