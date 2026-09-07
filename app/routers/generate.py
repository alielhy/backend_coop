from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import LANGS
from app.models.models import Cooperative
from app.services.generator import render_preview, generate_site

router = APIRouter(prefix="/cooperatives/{cooperative_id}", tags=["generate"])


@router.get("/preview", response_class=HTMLResponse)
def preview(cooperative_id: int, lang: str = Query("fr"), db: Session = Depends(get_db)):
    if lang not in LANGS:
        raise HTTPException(400, f"lang must be one of {LANGS}")
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    return render_preview(coop, lang)


@router.post("/generate")
def generate(cooperative_id: int, db: Session = Depends(get_db)):
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    zip_path = generate_site(coop)
    return FileResponse(
        path=zip_path,
        filename=f"{coop.slug}.zip",
        media_type="application/zip",
    )