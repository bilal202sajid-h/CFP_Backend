import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


logger = logging.getLogger(__name__)


def list_frontend_configs(db: Session):
    logger.info("list_frontend_configs_query_start")
    configs = db.query(models.FrontendConfig).all()
    logger.info("list_frontend_configs_query_end count=%s", len(configs))
    return configs


def get_frontend_config(db: Session, config_id: int):
    logger.info("get_frontend_config_query_start config_id=%s", config_id)
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.id == config_id).first()
    if config is None:
        logger.warning("get_frontend_config_not_found config_id=%s", config_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    logger.info("get_frontend_config_query_end config_id=%s found=true", config_id)
    return config


def get_frontend_config_by_key(db: Session, config_key: str):
    logger.info("get_frontend_config_by_key_query_start config_key=%s", config_key)
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.config_key == config_key).first()
    if config is None:
        logger.warning("get_frontend_config_by_key_not_found config_key=%s", config_key)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    logger.info("get_frontend_config_by_key_query_end config_key=%s found=true", config_key)
    return config


def create_frontend_config(db: Session, payload: schemas.FrontendConfigCreate):
    logger.info("create_frontend_config_start config_key=%s", payload.config_key)
    config = models.FrontendConfig(**payload.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    logger.info("create_frontend_config_end config_id=%s config_key=%s", config.id, config.config_key)
    return config


def update_frontend_config(db: Session, config_id: int, payload: schemas.FrontendConfigUpdate):
    logger.info("update_frontend_config_start config_id=%s fields=%s", config_id, list(payload.model_dump(exclude_unset=True).keys()))
    config = get_frontend_config(db, config_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    logger.info("update_frontend_config_end config_id=%s", config_id)
    return config


def update_frontend_config_by_key(db: Session, config_key: str, payload: schemas.FrontendConfigUpdate):
    logger.info("update_frontend_config_by_key_start config_key=%s fields=%s", config_key, list(payload.model_dump(exclude_unset=True).keys()))
    config = db.query(models.FrontendConfig).filter(models.FrontendConfig.config_key == config_key).first()
    data = payload.model_dump(exclude_unset=True)

    if config is None:
        logger.info("update_frontend_config_by_key_create config_key=%s", config_key)
        config = models.FrontendConfig(config_key=config_key, **data)
        db.add(config)
        db.commit()
        db.refresh(config)
        logger.info("update_frontend_config_by_key_end config_id=%s config_key=%s", config.id, config.config_key)
        return config

    for key, value in data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    logger.info("update_frontend_config_by_key_end config_id=%s config_key=%s", config.id, config.config_key)
    return config


def delete_frontend_config(db: Session, config_id: int):
    logger.info("delete_frontend_config_start config_id=%s", config_id)
    config = get_frontend_config(db, config_id)
    db.delete(config)
    db.commit()
    logger.info("delete_frontend_config_end config_id=%s", config_id)
