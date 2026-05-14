from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.security import require_admin
from ...db.session import get_db


router = APIRouter()


@router.get("/frontend-config", response_model=list[schemas.FrontendConfigRead])
def public_list_frontend_configs(db: Session = Depends(get_db)):
    return crud.list_frontend_configs(db)


@router.get("/frontend-config/{config_key}", response_model=schemas.FrontendConfigRead)
def public_get_frontend_config(config_key: str, db: Session = Depends(get_db)):
    return crud.get_frontend_config_by_key(db, config_key)


@router.post("/admin/frontend-config", response_model=schemas.FrontendConfigRead)
def admin_create_frontend_config(payload: schemas.FrontendConfigCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.create_frontend_config(db, payload)


@router.patch("/admin/frontend-config/{config_id}", response_model=schemas.FrontendConfigRead)
def admin_update_frontend_config(config_id: int, payload: schemas.FrontendConfigUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.update_frontend_config(db, config_id, payload)


@router.patch("/admin/frontend-config/key/{config_key}", response_model=schemas.FrontendConfigRead)
def admin_update_frontend_config_by_key(config_key: str, payload: schemas.FrontendConfigUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.update_frontend_config_by_key(db, config_key, payload)


@router.delete("/admin/frontend-config/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_frontend_config(config_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    crud.delete_frontend_config(db, config_id)
