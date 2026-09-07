from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Cooperative, Product, Media
from app.schemas.schemas import MediaOut
from app.services.storage import save_image, delete_image

router = APIRouter(prefix="/cooperatives/{cooperative_id}", tags=["media"])


@router.post("/media", response_model=MediaOut, status_code=201)
def upload_media(
    cooperative_id: int,
    type: str = Form(...),  # "logo" | "gallery"
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if type not in ("logo", "gallery"):
        raise HTTPException(400, "type must be 'logo' or 'gallery'")
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")

    relative_path = save_image(file, cooperative_id, type)
    media = Media(cooperative_id=cooperative_id, type=type, file_path=relative_path)
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/media/{media_id}", status_code=204)
def delete_media(cooperative_id: int, media_id: int, db: Session = Depends(get_db)):
    media = db.get(Media, media_id)
    if not media or media.cooperative_id != cooperative_id:
        raise HTTPException(404, "Media not found")
    delete_image(media.file_path)
    db.delete(media)
    db.commit()


@router.post("/products/{product_id}/photo", response_model=None, status_code=200)
def upload_product_photo(
    cooperative_id: int,
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product or product.cooperative_id != cooperative_id:
        raise HTTPException(404, "Product not found")
    if product.image_path:
        delete_image(product.image_path)
    product.image_path = save_image(file, cooperative_id, "products")
    db.commit()
    return {"image_path": product.image_path}