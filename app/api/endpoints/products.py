from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...db.session import get_db


router = APIRouter()


@router.get("/products", response_model=list[schemas.ProductRead])
def public_products(category: str | None = None, featured: bool | None = None, db: Session = Depends(get_db)):
    return crud.list_products(db, category=category, featured=featured)


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def public_product_detail(product_id: int, db: Session = Depends(get_db)):
    return crud.get_product(db, product_id)