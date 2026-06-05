from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", response_model=List[schemas.ProductResponse])
def get_all_products(
    search: Optional[str] = None, 
    category: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    Fetches all products. 
    Supports optional query parameters for search (name matching) and category filtering.
    """
    query = db.query(models.Product)
    
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    
    if category and category != "All":
        query = query.filter(models.Product.category == category)
        
    return query.all()


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_single_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific product by its ID. 
    Raises a 404 HTTP exception if the product does not exist.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found in the database."
        )
        
    return product


@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product record in the database.
    """
    new_product = models.Product(**product.model_dump())
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, updated_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Updates an existing product fully based on the provided ID.
    Raises a 404 HTTP exception if the target product is not found.
    """
    product_query = db.query(models.Product).filter(models.Product.id == product_id)
    existing_product = product_query.first()
    
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cannot update. Product not found."
        )
    
    # Update the fields using the incoming validated payload
    product_query.update(updated_data.model_dump(), synchronize_session=False)
    db.commit()
    
    return product_query.first()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Deletes a product from the database permanently.
    Raises a 404 HTTP exception if the product does not exist.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cannot delete. Product not found."
        )
        
    db.delete(product)
    db.commit()
    
    return {"message": "Product successfully deleted."}