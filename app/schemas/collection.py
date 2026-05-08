from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CollectionBase(BaseModel):
    title: str
    subtitle: str
    description: str
    image_url: str
    categories: list[str] = Field(default_factory=list)
    sort_order: int = 0


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    image_url: str | None = None
    categories: list[str] | None = None
    sort_order: int | None = None


class CollectionRead(CollectionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)