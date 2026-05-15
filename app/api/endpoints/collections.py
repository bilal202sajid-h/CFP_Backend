import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/collections", response_model=list[schemas.CollectionRead])
def public_collections(db: Session = Depends(get_db)):
    logger.info("public_collections_start")
    collections = crud.list_collections(db)
    logger.info("public_collections_end count=%s", len(collections))
    return collections


@router.get("/collections/{collection_id}", response_model=schemas.CollectionRead)
def public_collection_detail(collection_id: int, db: Session = Depends(get_db)):
    logger.info("public_collection_detail_start collection_id=%s", collection_id)
    collection = crud.get_collection(db, collection_id)
    logger.info("public_collection_detail_end collection_id=%s found=true", collection_id)
    return collection