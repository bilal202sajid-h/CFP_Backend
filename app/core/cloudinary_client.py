import os
from typing import BinaryIO

import cloudinary
import cloudinary.uploader

from .config import settings


_is_configured = False


def _configure_cloudinary() -> None:
    global _is_configured

    if _is_configured:
        return

    if settings.cloudinary_url:
        os.environ["CLOUDINARY_URL"] = settings.cloudinary_url
        cloudinary.config(secure=True)
        _is_configured = True
        return

    required_values = [
        settings.cloudinary_cloud_name,
        settings.cloudinary_api_key,
        settings.cloudinary_api_secret,
    ]

    if not all(required_values):
        raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET.")

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    _is_configured = True


def upload_image(file_obj: BinaryIO, folder: str | None = None) -> dict[str, str]:
    _configure_cloudinary()

    upload_result = cloudinary.uploader.upload(
        file_obj,
        folder=folder or settings.cloudinary_upload_folder,
        resource_type="image",
    )

    return {
        "image_url": upload_result["secure_url"],
        "public_id": upload_result["public_id"],
    }


def delete_image(public_id: str) -> dict[str, str]:
    _configure_cloudinary()

    delete_result = cloudinary.uploader.destroy(
        public_id,
        resource_type="image",
        invalidate=True,
    )

    return {
        "public_id": public_id,
        "result": str(delete_result.get("result", "unknown")),
    }
