from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import datetime
import enum

class ScanMethod(str, enum.Enum):
    VISUAL = "visual"
    CODE = "code"
    MANUAL = "manual"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1) # 1 for True, 0 for False (SQLite compatibility)
    
    cards = relationship("Card", back_populates="owner")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    game = Column(String)
    set_code = Column(String)
    card_number = Column(String)
    rarity = Column(String)
    price = Column(String)
    description = Column(String)
    image_url = Column(String)
    image_path = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="cards")

class CardReference(Base):
    __tablename__ = "card_reference"

    id = Column(Integer, primary_key=True, index=True)
    game = Column(String)
    set_code = Column(String)
    card_number = Column(String)
    name = Column(String)
    rarity = Column(String)

class ScanMetadata(Base):
    __tablename__ = "scan_metadata"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer)
    scan_method = Column(String) # Could use Enum but keeping simple for now
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
