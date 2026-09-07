from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Cooperative
from app.schemas.schemas import CooperativeIn, CooperativeUpdate, CooperativeOut

router = APIRouter(prefix="/cooperatives", tags=["cooperatives"])


@router.get("", response_model=list[CooperativeOut])
def list_cooperatives(db: Session = Depends(get_db)):
    return db.query(Cooperative).order_by(Cooperative.id.desc()).all()


@router.post("", response_model=CooperativeOut, status_code=201)
def create_cooperative(payload: CooperativeIn, db: Session = Depends(get_db)):
    if db.query(Cooperative).filter(Cooperative.slug == payload.slug).first():
        raise HTTPException(409, "A cooperative with this slug already exists")
    coop = Cooperative(**payload.model_dump(exclude_unset=True))
    db.add(coop)
    db.commit()
    db.refresh(coop)
    return coop


@router.get("/{cooperative_id}", response_model=CooperativeOut)
def get_cooperative(cooperative_id: int, db: Session = Depends(get_db)):
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    return coop


@router.patch("/{cooperative_id}", response_model=CooperativeOut)
def update_cooperative(cooperative_id: int, payload: CooperativeUpdate, db: Session = Depends(get_db)):
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(coop, field, value)
    db.commit()
    db.refresh(coop)
    return coop


@router.delete("/{cooperative_id}", status_code=204)
def delete_cooperative(cooperative_id: int, db: Session = Depends(get_db)):
    coop = db.get(Cooperative, cooperative_id)
    if not coop:
        raise HTTPException(404, "Cooperative not found")
    db.delete(coop)
    db.commit()