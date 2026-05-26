from pydantic import BaseModel, ConfigDict, Field


class ProductImageInput(BaseModel):
    image_url: str
    public_id: str | None = None
    label: str | None = None
    sort_order: int = 0
    is_cover: bool = False


class ProductImageRead(BaseModel):
    id: int
    image_url: str
    public_id: str | None = None
    label: str | None = None
    sort_order: int
    is_cover: bool

    model_config = ConfigDict(from_attributes=True)
