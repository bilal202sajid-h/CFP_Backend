import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.security import require_admin
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/frontend-config", response_model=list[schemas.FrontendConfigRead])
def public_list_frontend_configs(db: Session = Depends(get_db)):
    logger.info("public_frontend_configs_start")
    configs = crud.list_frontend_configs(db)
    logger.info("public_frontend_configs_end count=%s", len(configs))
    return configs


@router.get("/frontend-config/{config_key}", response_model=schemas.FrontendConfigRead)
def public_get_frontend_config(config_key: str, db: Session = Depends(get_db)):
    logger.info("public_frontend_config_detail_start config_key=%s", config_key)
    config = crud.get_frontend_config_by_key(db, config_key)
    logger.info("public_frontend_config_detail_end config_key=%s found=true", config_key)
    return config


@router.post("/admin/frontend-config", response_model=schemas.FrontendConfigRead)
def admin_create_frontend_config(payload: schemas.FrontendConfigCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_create_frontend_config_start config_key=%s", payload.config_key)
    return crud.create_frontend_config(db, payload)


@router.patch("/admin/frontend-config/{config_id}", response_model=schemas.FrontendConfigRead)
def admin_update_frontend_config(config_id: int, payload: schemas.FrontendConfigUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_update_frontend_config_start config_id=%s fields=%s", config_id, list(payload.model_dump(exclude_unset=True).keys()))
    return crud.update_frontend_config(db, config_id, payload)


@router.patch("/admin/frontend-config/key/{config_key}", response_model=schemas.FrontendConfigRead)
def admin_update_frontend_config_by_key(config_key: str, payload: schemas.FrontendConfigUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_update_frontend_config_by_key_start config_key=%s fields=%s", config_key, list(payload.model_dump(exclude_unset=True).keys()))
    return crud.update_frontend_config_by_key(db, config_key, payload)


@router.delete("/admin/frontend-config/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_frontend_config(config_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_delete_frontend_config_start config_id=%s", config_id)
    crud.delete_frontend_config(db, config_id)
