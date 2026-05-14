from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


def list_categories(db: Session):
    return db.query(models.Category).order_by(models.Category.sort_order.asc(), models.Category.id.asc()).all()


def get_category(db: Session, category_id: int):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def get_category_by_name(db: Session, name: str):
    category = db.query(models.Category).filter(models.Category.name == name).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def create_category(db: Session, payload: schemas.CategoryCreate):
    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: schemas.CategoryUpdate):
    category = get_category(db, category_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    db.delete(category)
    db.commit()
