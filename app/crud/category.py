import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


logger = logging.getLogger(__name__)


def list_categories(db: Session):
    logger.info("list_categories_query_start")
    categories = db.query(models.Category).order_by(models.Category.sort_order.asc(), models.Category.id.asc()).all()
    logger.info("list_categories_query_end count=%s", len(categories))
    return categories


def get_category(db: Session, category_id: int):
    logger.info("get_category_query_start category_id=%s", category_id)
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        logger.warning("get_category_not_found category_id=%s", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    logger.info("get_category_query_end category_id=%s found=true", category_id)
    return category


def get_category_by_name(db: Session, name: str):
    logger.info("get_category_by_name_query_start name=%s", name)
    category = db.query(models.Category).filter(models.Category.name == name).first()
    if category is None:
        logger.warning("get_category_by_name_not_found name=%s", name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    logger.info("get_category_by_name_query_end name=%s found=true", name)
    return category


def create_category(db: Session, payload: schemas.CategoryCreate):
    logger.info("create_category_start name=%s display_name=%s", payload.name, payload.display_name)
    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info("create_category_end category_id=%s", category.id)
    return category


def update_category(db: Session, category_id: int, payload: schemas.CategoryUpdate):
    logger.info("update_category_start category_id=%s fields=%s", category_id, list(payload.model_dump(exclude_unset=True).keys()))
    category = get_category(db, category_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    logger.info("update_category_end category_id=%s", category_id)
    return category


def delete_category(db: Session, category_id: int):
    logger.info("delete_category_start category_id=%s", category_id)
    category = get_category(db, category_id)
    db.delete(category)
    db.commit()
    logger.info("delete_category_end category_id=%s", category_id)
