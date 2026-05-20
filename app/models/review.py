from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text, func

from ..db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True, index=True)
    author_name = Column(String(120), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    city = Column(String(120), nullable=True)
    is_approved = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
