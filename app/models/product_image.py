from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from ..db.base import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = Column(Text, nullable=False)
    public_id = Column(String, nullable=True)
    label = Column(String, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_cover = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="images")
