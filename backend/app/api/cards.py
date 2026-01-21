from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.recognition import RecognitionService
from .. import schemas
from ..models import models
from .auth import get_current_user

router = APIRouter(prefix="/cards", tags=["cards"])

@router.post("/scan", response_model=schemas.ScanResponse)
async def scan_card(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = RecognitionService(db)
    contents = await file.read()
    result = await service.scan_card(contents)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.post("/", response_model=schemas.Card)
def create_card(
    card: schemas.CardCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_card = models.Card(**card.dict())
    db_card.owner_id = current_user.id
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.get("/", response_model=list[schemas.Card])
def get_cards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Card).filter(models.Card.owner_id == current_user.id).all()

@router.post("/train-ml")
async def train_ml_model(current_user: models.User = Depends(get_current_user)):
    # Placeholder for ML training trigger
    # In a real app, this would start a background task
    return {"status": "Training started", "message": f"ML model training initiated for user {current_user.email}."}
