from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    subtitle: str
    price: Decimal
    category: str
    description: str
    details: str | None = None
    image_url: str
    badge: str | None = None
    featured: bool = False
    collection_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    subtitle: str | None = None
    price: Decimal | None = None
    category: str | None = None
    description: str | None = None
    details: str | None = None
    image_url: str | None = None
    badge: str | None = None
    featured: bool | None = None
    collection_id: int | None = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)