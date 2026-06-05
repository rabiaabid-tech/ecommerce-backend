# models.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DECIMAL
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    image = Column(String(500), nullable=False) 
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False)
    old_price = Column(DECIMAL(10, 2), nullable=True)
    rating = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    free_shipping = Column(Boolean, default=True)