import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


logger = logging.getLogger(__name__)


def list_collections(db: Session):
    logger.info("list_collections_query_start")
    collections = db.query(models.Collection).order_by(models.Collection.sort_order.asc(), models.Collection.id.asc()).all()
    logger.info("list_collections_query_end count=%s", len(collections))
    return collections


def get_collection(db: Session, collection_id: int):
    logger.info("get_collection_query_start collection_id=%s", collection_id)
    collection = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if collection is None:
        logger.warning("get_collection_not_found collection_id=%s", collection_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    logger.info("get_collection_query_end collection_id=%s found=true", collection_id)
    return collection


def create_collection(db: Session, payload: schemas.CollectionCreate):
    logger.info("create_collection_start title=%s sort_order=%s", payload.title, payload.sort_order)
    collection = models.Collection(**payload.model_dump())
    db.add(collection)
    db.commit()
    db.refresh(collection)
    logger.info("create_collection_end collection_id=%s", collection.id)
    return collection


def update_collection(db: Session, collection_id: int, payload: schemas.CollectionUpdate):
    logger.info("update_collection_start collection_id=%s fields=%s", collection_id, list(payload.model_dump(exclude_unset=True).keys()))
    collection = get_collection(db, collection_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(collection, key, value)
    db.commit()
    db.refresh(collection)
    logger.info("update_collection_end collection_id=%s", collection_id)
    return collection


def delete_collection(db: Session, collection_id: int):
    logger.info("delete_collection_start collection_id=%s", collection_id)
    collection = get_collection(db, collection_id)
    db.delete(collection)
    db.commit()
    logger.info("delete_collection_end collection_id=%s", collection_id)