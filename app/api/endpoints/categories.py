from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.security import require_admin
from ...db.session import get_db


router = APIRouter()


@router.get("/categories", response_model=list[schemas.CategoryRead])
def public_list_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


@router.get("/categories/{category_id}", response_model=schemas.CategoryRead)
def public_get_category(category_id: int, db: Session = Depends(get_db)):
    return crud.get_category(db, category_id)


@router.post("/admin/categories", response_model=schemas.CategoryRead)
def admin_create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.create_category(db, payload)


@router.patch("/admin/categories/{category_id}", response_model=schemas.CategoryRead)
def admin_update_category(category_id: int, payload: schemas.CategoryUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.update_category(db, category_id, payload)


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_category(category_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    crud.delete_category(db, category_id)
