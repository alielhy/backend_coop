from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Cooperative, Product
from app.schemas.schemas import ProductIn, ProductOut

router = APIRouter(prefix="/cooperatives/{cooperative_id}/products", tags=["products"])


def _get_coop_or_404(cooperative_id: int, db: Session) -> Cooperative:
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    return coop


@router.get("", response_model=list[ProductOut])
def list_products(cooperative_id: int, db: Session = Depends(get_db)):
    _get_coop_or_404(cooperative_id, db)
    return (
        db.query(Product)
        .filter(Product.cooperative_id == cooperative_id)
        .order_by(Product.position)
        .all()
    )


@router.post("", response_model=ProductOut, status_code=201)
def create_product(cooperative_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    _get_coop_or_404(cooperative_id, db)
    product = Product(cooperative_id=cooperative_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(cooperative_id: int, product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or product.cooperative_id != cooperative_id:
        raise HTTPException(404, "Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(cooperative_id: int, product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or product.cooperative_id != cooperative_id:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    db.commit()