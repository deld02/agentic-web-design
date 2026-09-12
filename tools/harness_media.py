"""Bounded, decoded raster exchange and immutable media provenance."""

import base64
from hashlib import sha256
from io import BytesIO
from pathlib import Path

MAX_IMAGE_BYTES = 12 * 1024 * 1024
MIME = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
SUFFIX = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}


def inspect_raster(data: bytes, suffix: str) -> dict:
    from PIL import Image
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError("image is empty or exceeds 12 MiB")
    with Image.open(BytesIO(data)) as picture:
        if picture.format != SUFFIX.get(suffix.lower()) or picture.format not in MIME:
            raise ValueError("image format and extension do not match")
        width, height = picture.size
        if min(width, height) < 16 or max(width, height) > 16000 or width * height > 40_000_000:
            raise ValueError("unsupported image dimensions")
        picture.verify()
    with Image.open(BytesIO(data)) as picture:
        picture.load()
    return {"width": width, "height": height, "sha256": sha256(data).hexdigest(),
            "mimeType": MIME[SUFFIX[suffix.lower()]], "bytes": len(data)}


def image_content(path: Path) -> dict:
    data = path.read_bytes()
    metadata = inspect_raster(data, path.suffix)
    return {"type": "image", "mimeType": metadata["mimeType"],
            "data": base64.b64encode(data).decode("ascii")}
