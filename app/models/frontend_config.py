from sqlalchemy import BigInteger, Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from ..db.base import Base


class FrontendConfig(Base):
    __tablename__ = "frontend_configs"

    id = Column(BigInteger, primary_key=True, index=True)
    config_key = Column(String, unique=True, nullable=False, index=True)
    config_value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
