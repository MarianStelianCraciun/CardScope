from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CardBase(BaseModel):
    name: str
    game: str
    set_code: str
    card_number: str
    rarity: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CardCreate(CardBase):
    image_path: Optional[str] = None
    confidence: float

class Card(CardBase):
    id: int
    image_path: Optional[str] = None
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    scan_method: str
    confidence: float
    requires_confirmation: bool
    card_data: Optional[Card] = None
