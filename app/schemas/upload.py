from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_url: str
    public_id: str
