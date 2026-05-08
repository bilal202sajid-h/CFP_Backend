from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...db.session import get_db


router = APIRouter()


@router.get("/collections", response_model=list[schemas.CollectionRead])
def public_collections(db: Session = Depends(get_db)):
    return crud.list_collections(db)


@router.get("/collections/{collection_id}", response_model=schemas.CollectionRead)
def public_collection_detail(collection_id: int, db: Session = Depends(get_db)):
    return crud.get_collection(db, collection_id)