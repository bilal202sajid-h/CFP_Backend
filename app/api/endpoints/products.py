import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/products", response_model=list[schemas.ProductListRead])
def public_products(category: str | None = None, featured: bool | None = None, db: Session = Depends(get_db)):
    logger.info("public_products_start category=%s featured=%s", category, featured)
    products = crud.list_products(db, category=category, featured=featured)
    logger.info("public_products_end category=%s featured=%s count=%s", category, featured, len(products))
    return products


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def public_product_detail(product_id: int, db: Session = Depends(get_db)):
    logger.info("public_product_detail_start product_id=%s", product_id)
    product = crud.get_product(db, product_id, load_images=True)
    logger.info("public_product_detail_end product_id=%s found=true", product_id)
    return product