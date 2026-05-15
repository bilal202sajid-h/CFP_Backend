from typing import BinaryIO
from urllib.parse import unquote, urlparse
import logging

import cloudinary
import cloudinary.uploader

from .config import settings


logger = logging.getLogger(__name__)
_is_configured = False


def _clean(value: str | None) -> str | None:
    if not isinstance(value, str):
        return value

    cleaned = value.strip()

    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()

    return cleaned


def _parse_cloudinary_url(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)

    if parsed.scheme != "cloudinary" or not parsed.hostname or not parsed.username or not parsed.password:
        raise RuntimeError("Invalid CLOUDINARY_URL format. Expected cloudinary://<api_key>:<api_secret>@<cloud_name>")

    return parsed.hostname, unquote(parsed.username), unquote(parsed.password)


def _configure_cloudinary() -> None:
    global _is_configured

    if _is_configured:
        return

    cloudinary_url = _clean(settings.cloudinary_url)
    cloudinary_cloud_name = _clean(settings.cloudinary_cloud_name)
    cloudinary_api_key = _clean(settings.cloudinary_api_key)
    cloudinary_api_secret = _clean(settings.cloudinary_api_secret)

    logger.info(
        "cloudinary_config_start cloud_name_set=%s api_key_set=%s api_secret_set=%s url_set=%s",
        bool(cloudinary_cloud_name),
        bool(cloudinary_api_key),
        bool(cloudinary_api_secret),
        bool(cloudinary_url),
    )

    # Prefer explicit values so production can override a stale CLOUDINARY_URL.
    if not all([cloudinary_cloud_name, cloudinary_api_key, cloudinary_api_secret]):
        if cloudinary_url:
            cloudinary_cloud_name, cloudinary_api_key, cloudinary_api_secret = _parse_cloudinary_url(cloudinary_url)
        else:
            raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET.")

    cloudinary.config(
        cloud_name=cloudinary_cloud_name,
        api_key=cloudinary_api_key,
        api_secret=cloudinary_api_secret,
        secure=True,
    )
    logger.info("cloudinary_config_end cloud_name=%s upload_folder=%s", cloudinary_cloud_name, settings.cloudinary_upload_folder)
    _is_configured = True


def upload_image(file_obj: BinaryIO, folder: str | None = None) -> dict[str, str]:
    _configure_cloudinary()

    upload_folder = folder or settings.cloudinary_upload_folder
    logger.info("cloudinary_upload_start folder=%s", upload_folder)

    upload_result = cloudinary.uploader.upload(
        file_obj,
        folder=upload_folder,
        resource_type="image",
    )

    logger.info("cloudinary_upload_end public_id=%s", upload_result.get("public_id"))

    return {
        "image_url": upload_result["secure_url"],
        "public_id": upload_result["public_id"],
    }


def delete_image(public_id: str) -> dict[str, str]:
    _configure_cloudinary()

    logger.info("cloudinary_delete_start public_id=%s", public_id)

    delete_result = cloudinary.uploader.destroy(
        public_id,
        resource_type="image",
        invalidate=True,
    )

    logger.info("cloudinary_delete_end public_id=%s result=%s", public_id, delete_result.get("result"))

    return {
        "public_id": public_id,
        "result": str(delete_result.get("result", "unknown")),
    }
