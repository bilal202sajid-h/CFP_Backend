from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import logging

from .. import models, schemas


logger = logging.getLogger(__name__)


def list_products(db: Session, category: str | None = None, featured: bool | None = None):
    logger.info("list_products_query_start category=%s featured=%s", category, featured)
    query = db.query(models.Product).filter(models.Product.is_admin_uploaded == True)
    if category:
        query = query.filter(models.Product.category == category)
    if featured is not None:
        query = query.filter(models.Product.featured == featured)

    products = query.order_by(models.Product.id.asc()).all()
    logger.info("list_products_query_end category=%s featured=%s count=%s", category, featured, len(products))
    return products


def get_product(db: Session, product_id: int):
    logger.info("get_product_query_start product_id=%s", product_id)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        logger.warning("get_product_not_found product_id=%s", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    logger.info("get_product_query_end product_id=%s found=true", product_id)
    return product


def create_product(db: Session, payload: schemas.ProductCreate):
    logger.info("create_product_start category=%s featured=%s has_image=%s", payload.category, payload.featured, bool(payload.image_url))
    product = models.Product(**payload.model_dump())
    # Mark products created via admin API as admin-uploaded so they appear in public listings
    product.is_admin_uploaded = True
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info("create_product_end product_id=%s", product.id)
    return product


def update_product(db: Session, product_id: int, payload: schemas.ProductUpdate):
    logger.info("update_product_start product_id=%s fields=%s", product_id, list(payload.model_dump(exclude_unset=True).keys()))
    product = get_product(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    logger.info("update_product_end product_id=%s", product_id)
    return product


def delete_product(db: Session, product_id: int):
    logger.info("delete_product_start product_id=%s", product_id)
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
    logger.info("delete_product_end product_id=%s", product_id)