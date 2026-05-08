from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


def list_products(db: Session, category: str | None = None, featured: bool | None = None):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    if featured is not None:
        query = query.filter(models.Product.featured == featured)
    return query.order_by(models.Product.id.asc()).all()


def get_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, payload: schemas.ProductCreate):
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, payload: schemas.ProductUpdate):
    product = get_product(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()