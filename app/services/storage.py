import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from app.core.config import MEDIA_DIR

MAX_DIMENSION = 1600  # px, longest side — keeps zip downloads reasonable


def save_image(file: UploadFile, cooperative_id: int, subfolder: str) -> str:
    """Save + downscale an uploaded image. Returns the path relative to
    MEDIA_DIR, e.g. '3/products/ab12cd34.jpg' — this is what gets stored
    in Product.image_path / Media.file_path."""
    dest_dir = MEDIA_DIR / str(cooperative_id) / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    dest_path = dest_dir / filename

    image = Image.open(file.file)
    image = image.convert("RGB") if image.mode in ("P", "RGBA") and ext in (".jpg", ".jpeg") else image
    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    image.save(dest_path, quality=85, optimize=True)

    return f"{cooperative_id}/{subfolder}/{filename}"


def delete_image(relative_path: str) -> None:
    path = MEDIA_DIR / relative_path
    if path.exists():
        path.unlink()