from sqlalchemy.orm import Session

from .. import models
from ..core.security import verify_password


def get_admin_by_username(db: Session, username: str):
    return db.query(models.AdminUser).filter(models.AdminUser.username == username).first()


def get_admin_by_id(db: Session, admin_id: int):
    return db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()


def authenticate_admin(db: Session, username: str, password: str):
    admin = get_admin_by_username(db, username)
    if not admin or not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin