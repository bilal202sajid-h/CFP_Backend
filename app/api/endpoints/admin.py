from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.cloudinary_client import delete_image, upload_image
from ...core.security import create_access_token, require_admin
from ...db.session import get_db


router = APIRouter()


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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")

    try:
        result = upload_image(file.file)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Cloudinary upload failed: {exc}") from exc

    return schemas.ImageUploadResponse(**result)


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
    return crud.create_product(db, payload)


@router.patch("/admin/products/{product_id}", response_model=schemas.ProductRead)
def admin_update_product(product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return crud.update_product(db, product_id, payload)


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_product(product_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    crud.delete_product(db, product_id)