import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


logger = logging.getLogger(__name__)

SEED_REVIEWS = [
    {
        "author_name": "Ayesha Khan",
        "rating": 5,
        "comment": "We ordered a solid wood bed and wardrobe set. Delivery was on time and the finishing is excellent. Very happy with the quality for the price.",
        "city": "Lahore",
        "is_approved": True,
    },
    {
        "author_name": "Hassan Raza",
        "rating": 5,
        "comment": "Bought a dining table with six chairs. Strong build, smooth polish, and the team helped us choose the right size for our dining room.",
        "city": "Faisalabad",
        "is_approved": True,
    },
    {
        "author_name": "Fatima Ali",
        "rating": 4,
        "comment": "Sofa set looks beautiful in our lounge. Comfortable for daily family use and the wood frame feels very sturdy.",
        "city": "Chiniot",
        "is_approved": True,
    },
]


def seed_reviews_if_empty(db: Session) -> None:
    count = db.query(models.Review).count()
    if count > 0:
        return
    logger.info("seed_reviews_start count=%s", len(SEED_REVIEWS))
    for item in SEED_REVIEWS:
        db.add(models.Review(**item))
    db.commit()
    logger.info("seed_reviews_end")


def list_reviews(db: Session, *, skip: int = 0, limit: int = 50, approved_only: bool = True):
    query = db.query(models.Review)
    if approved_only:
        query = query.filter(models.Review.is_approved.is_(True))
    return (
        query.order_by(models.Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_review(db: Session, review_id: int):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


def create_review(db: Session, payload: schemas.ReviewCreate):
    review = models.Review(**payload.model_dump(), is_approved=True)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int):
    review = get_review(db, review_id)
    db.delete(review)
    db.commit()
