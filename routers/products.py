from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas, auth_utils  

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# ─── PUBLIC ROUTES (Any user can access) ───

@router.get("/", response_model=List[schemas.ProductResponse])
def get_all_products(
    search: Optional[str] = None, 
    category: Optional[str] = None,
    skip: int = 0,       
    limit: int = 10,  
    db: Session = Depends(get_db)
):
    """
    Fetches all products. 
    Supports optional query parameters for search and category filtering.
    """
    query = db.query(models.Product)
    
    if search:
     query = query.filter(
        models.Product.name.ilike(f"%{search}%") |
        models.Product.description.ilike(f"%{search}%") |
        models.Product.category.ilike(f"%{search}%")
    )
    
    if category and category != "All":
        query = query.filter(models.Product.category == category)
        
    total = query.count() 
    products = query.offset(skip).limit(limit).all()

    return products


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_single_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific product by its ID. 
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found in the database."
        )
        
    return product


# ─── PROTECTED ROUTES (Only Admins can access) ───

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    admin: dict = Depends(auth_utils.get_current_admin)  # 🔒 ADMIN GUARD
):
    """
    Creates a new product record. Admin access required.
    """
    new_product = models.Product(**product.model_dump())
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int, 
    updated_data: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    admin: dict = Depends(auth_utils.get_current_admin)  # 🔒 ADMIN GUARD
):
    """
    Updates an existing product. Admin access required.
    """
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot update. Product not found."
        )

    for key, value in updated_data.model_dump(
        exclude_unset=True
    ).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    admin: dict = Depends(auth_utils.get_current_admin)  # 🔒 ADMIN GUARD
):
    """
    Deletes a product permanently. Admin access required.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cannot delete. Product not found."
        )
        
    db.delete(product)
    db.commit()
    