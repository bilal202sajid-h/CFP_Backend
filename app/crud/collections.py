from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


def list_collections(db: Session):
    return db.query(models.Collection).order_by(models.Collection.sort_order.asc(), models.Collection.id.asc()).all()


def get_collection(db: Session, collection_id: int):
    collection = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


def create_collection(db: Session, payload: schemas.CollectionCreate):
    collection = models.Collection(**payload.model_dump())
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def update_collection(db: Session, collection_id: int, payload: schemas.CollectionUpdate):
    collection = get_collection(db, collection_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(collection, key, value)
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection_id: int):
    collection = get_collection(db, collection_id)
    db.delete(collection)
    db.commit()