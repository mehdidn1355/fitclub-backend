from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "popular",
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)

    if category and category != "all":
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.title.contains(search))

    if sort == "price-low":
        query = query.order_by(Product.price.asc())
    elif sort == "price-high":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())

    return query.all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product