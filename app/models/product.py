from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from ..db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subtitle = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    image_url = Column(Text, nullable=False)
    badge = Column(String, nullable=True)
    featured = Column(Boolean, nullable=False, default=False, index=True)
    collection_id = Column(BigInteger, ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    collection = relationship("Collection", back_populates="products")