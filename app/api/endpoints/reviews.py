import logging

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...core.security import require_admin
from ...db.session import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/reviews", response_model=list[schemas.ReviewRead])
def public_list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.info("public_reviews_start skip=%s limit=%s", skip, limit)
    reviews = crud.list_reviews(db, skip=skip, limit=limit, approved_only=True)
    logger.info("public_reviews_end count=%s", len(reviews))
    return reviews


@router.post("/reviews", response_model=schemas.ReviewRead, status_code=status.HTTP_201_CREATED)
def public_create_review(payload: schemas.ReviewCreate, db: Session = Depends(get_db)):
    logger.info("public_create_review_start author=%s rating=%s", payload.author_name, payload.rating)
    review = crud.create_review(db, payload)
    logger.info("public_create_review_end review_id=%s", review.id)
    return review


@router.get("/admin/reviews", response_model=list[schemas.ReviewRead])
def admin_list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return crud.list_reviews(db, skip=skip, limit=limit, approved_only=False)


@router.delete("/admin/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    crud.delete_review(db, review_id)
