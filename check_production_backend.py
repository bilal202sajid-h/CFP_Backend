from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://cfp-backend-a7wo.onrender.com/api"


ONE_BY_ONE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO9X2lsAAAAASUVORK5CYII="
)


@dataclass
class ResponseData:
    status: int
    body: Any


def normalize_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if not normalized.endswith("/api"):
        normalized = f"{normalized}/api"
    return normalized


def request_json(method: str, url: str, headers: dict[str, str] | None = None, data: bytes | None = None) -> ResponseData:
    request = Request(url, data=data, headers=headers or {}, method=method)

    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            body = json.loads(raw) if raw else None
            return ResponseData(status=response.status, body=body)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw
        return ResponseData(status=exc.code, body=body)
    except URLError as exc:
        raise RuntimeError(f"Network error while calling {url}: {exc}") from exc


def encode_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload).encode("utf-8")


def build_multipart_form(file_name: str, field_name: str, content_type: str, content: bytes) -> tuple[str, bytes]:
    boundary = f"----cfp-boundary-{uuid.uuid4().hex}"
    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_name}"\r\n'.encode("utf-8"),
        f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
        content,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return boundary, b"".join(parts)


def print_result(label: str, response: ResponseData) -> None:
    print(f"{label}: HTTP {response.status}")
    if response.body is not None:
        print(json.dumps(response.body, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the production backend and Cloudinary upload path.")
    parser.add_argument("--base-url", default=os.getenv("BACKEND_BASE_URL", DEFAULT_BASE_URL), help="Backend base URL")
    parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME"), help="Admin username")
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"), help="Admin password")
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Only check health and optional login, then stop before uploading an image.",
    )
    parser.add_argument(
        "--debug-cloudinary",
        action="store_true",
        help="After login, call the admin Cloudinary diagnostics endpoint before upload.",
    )
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    health_url = urljoin(base_url + "/", "health")

    print(f"Checking backend health at {health_url} ...")
    health = request_json("GET", health_url)
    print_result("Health check", health)

    if health.status != 200 or not isinstance(health.body, dict) or health.body.get("status") != "ok":
        print("Health check failed.")
        return 1

    if args.skip_upload:
        print("Skip-upload mode requested. Backend health looks good.")
        return 0

    if not args.username or not args.password:
        print("Admin credentials were not provided, so the authenticated upload check was skipped.")
        print("Set ADMIN_USERNAME and ADMIN_PASSWORD, or pass --username and --password, to verify Cloudinary upload.")
        return 0

    login_url = urljoin(base_url + "/", "admin/login")
    print(f"Logging in at {login_url} ...")
    login = request_json(
        "POST",
        login_url,
        headers={"Content-Type": "application/json"},
        data=encode_json({"username": args.username, "password": args.password}),
    )
    print_result("Login", login)

    if login.status != 200 or not isinstance(login.body, dict) or "access_token" not in login.body:
        print("Login failed, so the upload check could not run.")
        return 1

    token = login.body["access_token"]

    if args.debug_cloudinary:
        debug_url = urljoin(base_url + "/", "admin/debug/cloudinary")
        print(f"Checking Cloudinary runtime settings at {debug_url} ...")
        debug_response = request_json(
            "GET",
            debug_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        print_result("Cloudinary debug", debug_response)

        if debug_response.status != 200:
            print("Cloudinary diagnostics failed.")
            return 1

    upload_url = urljoin(base_url + "/", "admin/uploads/product-image")
    boundary, multipart_body = build_multipart_form(
        file_name="smoke-test.png",
        field_name="file",
        content_type="image/png",
        content=ONE_BY_ONE_PNG,
    )
    print(f"Uploading test image to {upload_url} ...")
    upload = request_json(
        "POST",
        upload_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        data=multipart_body,
    )
    print_result("Upload", upload)

    if upload.status != 200:
        detail = upload.body.get("detail") if isinstance(upload.body, dict) else None
        if isinstance(detail, str) and "Invalid Signature" in detail:
            print("Cloudinary signature is still wrong in production.")
            return 1

        print("Upload failed.")
        return 1

    if isinstance(upload.body, dict) and upload.body.get("image_url") and upload.body.get("public_id"):
        print("Production backend upload path is working.")
        return 0

    print("Upload returned an unexpected payload.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())