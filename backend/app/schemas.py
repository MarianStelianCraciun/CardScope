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
    owner_id: Optional[int] = None

class Card(CardBase):
    id: int
    owner_id: Optional[int] = None
    image_path: Optional[str] = None
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ScanResponse(BaseModel):
    scan_method: str
    confidence: float
    requires_confirmation: bool
    card_data: Optional[Card] = None
