from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import models

def load_reference_data():
    db = SessionLocal()
    # Sample data for testing
    sample_cards = [
        {
            "game": "Yu-Gi-Oh!",
            "set_code": "LOB",
            "card_number": "001",
            "name": "Blue-Eyes White Dragon",
            "rarity": "Ultra Rare"
        },
        {
            "game": "Pokemon",
            "set_code": "SV1",
            "card_number": "025",
            "name": "Pikachu",
            "rarity": "Rare"
        }
    ]
    
    for card_data in sample_cards:
        # Check if already exists
        exists = db.query(models.CardReference).filter(
            models.CardReference.set_code == card_data["set_code"],
            models.CardReference.card_number == card_data["card_number"]
        ).first()
        
        if not exists:
            card = models.CardReference(**card_data)
            db.add(card)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    load_reference_data()
    print("Sample reference data loaded.")
