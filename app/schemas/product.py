from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .product_image import ProductImageInput, ProductImageRead


class ProductBase(BaseModel):
    name: str
    subtitle: str
    article_number: str = ""
    price: str
    category: str
    description: str
    details: str | None = None
    image_url: str
    badge: str | None = None
    featured: bool = False
    collection_id: int | None = None
    material: str | None = None
    dimensions: str | None = None
    stock: int = 0


class ProductCreate(ProductBase):
    images: list[ProductImageInput] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = None
    subtitle: str | None = None
    article_number: str | None = None
    price: str | None = None
    category: str | None = None
    description: str | None = None
    details: str | None = None
    image_url: str | None = None
    badge: str | None = None
    featured: bool | None = None
    collection_id: int | None = None
    material: str | None = None
    dimensions: str | None = None
    stock: int | None = None
    images: list[ProductImageInput] | None = None


class ProductListRead(ProductBase):
    id: int
    is_admin_uploaded: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductRead(ProductListRead):
    images: list[ProductImageRead] = Field(default_factory=list)