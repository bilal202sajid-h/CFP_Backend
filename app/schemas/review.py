from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    author_name: str = Field(min_length=2, max_length=120)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=2000)
    city: str | None = Field(default=None, max_length=120)


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
    is_approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
