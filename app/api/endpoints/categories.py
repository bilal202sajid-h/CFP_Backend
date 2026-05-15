import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.security import require_admin
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/categories", response_model=list[schemas.CategoryRead])
def public_list_categories(db: Session = Depends(get_db)):
    logger.info("public_categories_start")
    categories = crud.list_categories(db)
    logger.info("public_categories_end count=%s", len(categories))
    return categories


@router.get("/categories/{category_id}", response_model=schemas.CategoryRead)
def public_get_category(category_id: int, db: Session = Depends(get_db)):
    logger.info("public_category_detail_start category_id=%s", category_id)
    category = crud.get_category(db, category_id)
    logger.info("public_category_detail_end category_id=%s found=true", category_id)
    return category


@router.post("/admin/categories", response_model=schemas.CategoryRead)
def admin_create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_create_category_start name=%s display_name=%s", payload.name, payload.display_name)
    return crud.create_category(db, payload)


@router.patch("/admin/categories/{category_id}", response_model=schemas.CategoryRead)
def admin_update_category(category_id: int, payload: schemas.CategoryUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_update_category_start category_id=%s fields=%s", category_id, list(payload.model_dump(exclude_unset=True).keys()))
    return crud.update_category(db, category_id, payload)


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_category(category_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_delete_category_start category_id=%s", category_id)
    crud.delete_category(db, category_id)
