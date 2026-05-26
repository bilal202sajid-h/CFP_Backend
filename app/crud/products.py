import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas


logger = logging.getLogger(__name__)


def _normalize_image_inputs(
    images: list[schemas.ProductImageInput] | None,
    image_url: str | None,
) -> list[schemas.ProductImageInput]:
    if images:
        return images
    if image_url:
        return [schemas.ProductImageInput(image_url=image_url, is_cover=True, sort_order=0)]
    return []


def _resolve_cover_url(images: list[schemas.ProductImageInput]) -> str | None:
    if not images:
        return None
    for img in images:
        if img.is_cover:
            return img.image_url
    return images[0].image_url


def _sync_product_images(
    db: Session,
    product: models.Product,
    images: list[schemas.ProductImageInput],
) -> None:
    product.images.clear()
    cover_url = _resolve_cover_url(images)
    has_cover = any(img.is_cover for img in images)

    for index, img in enumerate(images):
        is_cover = img.is_cover if has_cover else index == 0
        product.images.append(
            models.ProductImage(
                image_url=img.image_url,
                public_id=img.public_id,
                label=img.label,
                sort_order=img.sort_order if img.sort_order else index,
                is_cover=is_cover,
            )
        )

    if cover_url:
        product.image_url = cover_url


def list_products(db: Session, category: str | None = None, featured: bool | None = None):
    logger.info("list_products_query_start category=%s featured=%s", category, featured)
    query = db.query(models.Product).filter(models.Product.is_admin_uploaded == True)
    if category:
        query = query.filter(models.Product.category == category)
    if featured is not None:
        query = query.filter(models.Product.featured == featured)

    products = query.order_by(models.Product.id.asc()).all()
    logger.info("list_products_query_end category=%s featured=%s count=%s", category, featured, len(products))
    return products


def get_product(db: Session, product_id: int, *, load_images: bool = False):
    logger.info("get_product_query_start product_id=%s", product_id)
    query = db.query(models.Product)
    if load_images:
        query = query.options(joinedload(models.Product.images))
    product = query.filter(models.Product.id == product_id).first()
    if product is None:
        logger.warning("get_product_not_found product_id=%s", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    logger.info("get_product_query_end product_id=%s found=true", product_id)
    return product


def create_product(db: Session, payload: schemas.ProductCreate):
    logger.info(
        "create_product_start category=%s featured=%s article_number=%s image_count=%s",
        payload.category,
        payload.featured,
        payload.article_number,
        len(payload.images),
    )
    data = payload.model_dump(exclude={"images"})
    images = _normalize_image_inputs(payload.images, payload.image_url)
    cover_url = _resolve_cover_url(images)
    if not cover_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one product image is required",
        )
    data["image_url"] = cover_url

    product = models.Product(**data)
    product.is_admin_uploaded = True
    db.add(product)
    try:
        db.flush()
        _sync_product_images(db, product, images)
        db.commit()
        db.refresh(product)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("create_product_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Could not save product. The database may need the latest schema "
                "(article_number, price columns). Redeploy the backend or run Backend/sql/schema.sql. "
                f"Error: {exc.orig if getattr(exc, 'orig', None) else str(exc)}"
            ),
        ) from exc
    logger.info("create_product_end product_id=%s", product.id)
    return get_product(db, product.id, load_images=True)


def update_product(db: Session, product_id: int, payload: schemas.ProductUpdate):
    logger.info("update_product_start product_id=%s fields=%s", product_id, list(payload.model_dump(exclude_unset=True).keys()))
    product = get_product(db, product_id, load_images=True)
    data = payload.model_dump(exclude_unset=True, exclude={"images"})
    for key, value in data.items():
        setattr(product, key, value)

    if payload.images is not None:
        images = _normalize_image_inputs(payload.images, product.image_url)
        if not images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one product image is required",
            )
        cover_url = _resolve_cover_url(images)
        if cover_url:
            product.image_url = cover_url
        _sync_product_images(db, product, images)
    elif "image_url" in data and payload.images is None:
        existing = list(product.images)
        if existing:
            cover = next((img for img in existing if img.is_cover), existing[0])
            cover.image_url = data["image_url"]
        elif data["image_url"]:
            _sync_product_images(
                db,
                product,
                [schemas.ProductImageInput(image_url=data["image_url"], is_cover=True, sort_order=0)],
            )

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("update_product_failed product_id=%s", product_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update product. Error: {exc.orig if getattr(exc, 'orig', None) else str(exc)}",
        ) from exc
    logger.info("update_product_end product_id=%s", product_id)
    return get_product(db, product_id, load_images=True)


def delete_product(db: Session, product_id: int):
    logger.info("delete_product_start product_id=%s", product_id)
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
    logger.info("delete_product_end product_id=%s", product_id)
