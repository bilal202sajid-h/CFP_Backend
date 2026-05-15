from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
import logging

from ... import crud, schemas
from ...core.cloudinary_client import delete_image, upload_image
from ...core.config import settings
from ...core.security import create_access_token, require_admin
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


def _mask_value(value: str | None, visible: int = 4) -> str | None:
    if not value:
        return None

    if len(value) <= visible:
        return "*" * len(value)

    return f"{value[:visible]}***{value[-visible:]}"


@router.get("/admin")
def admin_login_hint() -> dict[str, str]:
    return {"message": "POST username and password to /admin to receive a JWT access token."}


@router.post("/admin", response_model=schemas.TokenResponse)
@router.post("/admin/login", response_model=schemas.TokenResponse)
def admin_login(payload: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    admin = crud.authenticate_admin(db, payload.username, payload.password)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return schemas.TokenResponse(
        access_token=create_access_token(subject=str(admin.id), username=admin.username),
    )


@router.get("/admin/me", response_model=schemas.AdminPublic)
def admin_me(admin_payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    admin = crud.get_admin_by_id(db, int(admin_payload["sub"]))
    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


@router.post("/admin/uploads/product-image", response_model=schemas.ImageUploadResponse)
def admin_upload_product_image(file: UploadFile = File(...), _: dict = Depends(require_admin)):
    logger.info(
        "admin_upload_product_image_start filename=%s content_type=%s",
        file.filename,
        file.content_type,
    )
    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning("admin_upload_product_image_invalid_file filename=%s content_type=%s", file.filename, file.content_type)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")

    try:
        result = upload_image(file.file)
    except RuntimeError as exc:
        logger.exception("admin_upload_product_image_runtime_error filename=%s error=%s", file.filename, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("admin_upload_product_image_failed filename=%s error=%s", file.filename, exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Cloudinary upload failed: {exc}") from exc

    logger.info("admin_upload_product_image_end filename=%s public_id=%s", file.filename, result.get("public_id"))

    return schemas.ImageUploadResponse(**result)


@router.get("/admin/debug/cloudinary")
def admin_debug_cloudinary(_: dict = Depends(require_admin)):
    return {
        "cloudinary_cloud_name": _mask_value(settings.cloudinary_cloud_name),
        "cloudinary_api_key": _mask_value(settings.cloudinary_api_key),
        "cloudinary_api_secret_set": bool(settings.cloudinary_api_secret),
        "cloudinary_url_set": bool(settings.cloudinary_url),
        "cloudinary_upload_folder": settings.cloudinary_upload_folder,
    }


@router.delete("/admin/uploads/product-image")
def admin_delete_product_image(public_id: str, _: dict = Depends(require_admin)):
    try:
        result = delete_image(public_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Cloudinary delete failed: {exc}") from exc

    return result


@router.post("/admin/collections", response_model=schemas.CollectionRead)
def admin_create_collection(payload: schemas.CollectionCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.create_collection(db, payload)


@router.patch("/admin/collections/{collection_id}", response_model=schemas.CollectionRead)
def admin_update_collection(collection_id: int, payload: schemas.CollectionUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.update_collection(db, collection_id, payload)


@router.delete("/admin/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_collection(collection_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    crud.delete_collection(db, collection_id)


@router.post("/admin/products", response_model=schemas.ProductRead)
def admin_create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_create_product_start name=%s category=%s featured=%s", payload.name, payload.category, payload.featured)
    return crud.create_product(db, payload)


@router.patch("/admin/products/{product_id}", response_model=schemas.ProductRead)
def admin_update_product(product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_update_product_start product_id=%s fields=%s", product_id, list(payload.model_dump(exclude_unset=True).keys()))
    return crud.update_product(db, product_id, payload)


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_product(product_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    logger.info("admin_delete_product_start product_id=%s", product_id)
    crud.delete_product(db, product_id)