from pydantic import BaseModel, EmailStr
from typing import Optional

# ─── PRODUCT SCHEMAS ───
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

# ─── USER SCHEMAS ───
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str