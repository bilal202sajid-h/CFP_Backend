from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


def list_frontend_configs(db: Session):
    return db.query(models.FrontendConfig).all()


def get_frontend_config(db: Session, config_id: int):
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.id == config_id).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return config


def get_frontend_config_by_key(db: Session, config_key: str):
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.config_key == config_key).first()
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return config


def create_frontend_config(db: Session, payload: schemas.FrontendConfigCreate):
    config = models.FrontendConfig(**payload.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_frontend_config(db: Session, config_id: int, payload: schemas.FrontendConfigUpdate):
    config = get_frontend_config(db, config_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


def update_frontend_config_by_key(db: Session, config_key: str, payload: schemas.FrontendConfigUpdate):
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.config_key == config_key).first()
    data = payload.model_dump(exclude_unset=True)

    if config is None:
        config = models.FrontendConfig(config_key=config_key, **data)
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    for key, value in data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


def delete_frontend_config(db: Session, config_id: int):
    config = get_frontend_config(db, config_id)
    db.delete(config)
    db.commit()
