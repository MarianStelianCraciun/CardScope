from sqlalchemy.orm import Session
from ..models import models
from .. import schemas
from ..cv.processor import CVProcessor
from .external_api import ExternalCardAPI
from .s3_service import S3Service
import re
import uuid

class RecognitionService:
    def __init__(self, db: Session):
        self.db = db
        self.cv = CVProcessor()
        self.external_api = ExternalCardAPI()
        self.s3 = S3Service()

    async def scan_card(self, image_bytes: bytes):
        # 0. Upload image to S3 (if configured)
        s3_url = self.s3.upload_image(image_bytes, f"scans/{uuid.uuid4()}.jpg")

        # 1. Try Primary Path (Visual)
        cv_result = self.cv.process_image(image_bytes)
        if not cv_result:
            return {"error": "Failed to process image"}
        
        full_text = cv_result["text"]
        img = cv_result["image"]
        
        # Simple fuzzy matching or direct lookup (mocked for now)
        # In real case, we'd search CardReference by name extracted from full_text
        
        # 2. Try Failsafe Path (Card Code)
        code_text = self.cv.extract_card_code(img)
        detected_code = self._parse_card_code(code_text)
        
        if detected_code:
            # Lookup in DB
            reference = self.db.query(models.CardReference).filter(
                models.CardReference.set_code == detected_code['set'],
                models.CardReference.card_number == detected_code['number']
            ).first()
            
            # Even if not in local reference DB, try external API
            game_guess = "Yu-Gi-Oh!" if "-" in f"{detected_code['set']}-{detected_code['number']}" else "Pokemon"
            # Actually our regexes are generic. Let's try to be smart or just try both.
            # For now, let's use the reference if found, otherwise try external with a guess.
            
            external_data = None
            if reference:
                external_data = await self.external_api.get_card_details(
                    reference.game, reference.set_code, reference.card_number
                )
                
                card_data = {
                    "name": reference.name,
                    "game": reference.game,
                    "set_code": reference.set_code,
                    "card_number": reference.card_number,
                    "rarity": reference.rarity,
                }
                
                if external_data:
                    card_data.update(external_data)
                
                if s3_url:
                    card_data["image_path"] = s3_url

                return {
                    "scan_method": "code",
                    "confidence": 1.0,
                    "requires_confirmation": False,
                    "card_data": card_data
                }
            else:
                # Try external API directly with detected code
                # Try Yu-Gi-Oh! first as it's common
                external_data = await self.external_api.get_card_details(
                    "Yu-Gi-Oh!", detected_code['set'], detected_code['number']
                )
                if not external_data:
                    # Try Pokemon
                    external_data = await self.external_api.get_card_details(
                        "Pokemon", detected_code['set'], detected_code['number']
                    )
                
                if external_data:
                    card_data = {
                        "game": "Yu-Gi-Oh!" if "Yu-Gi-Oh!" in str(external_data) else "Pokemon", # Simple heuristic
                        "set_code": detected_code['set'],
                        "card_number": detected_code['number'],
                    }
                    card_data.update(external_data)
                    
                    if s3_url:
                        card_data["image_path"] = s3_url

                    return {
                        "scan_method": "code",
                        "confidence": 0.9,
                        "requires_confirmation": True,
                        "card_data": card_data
                    }

        # 3. Fallback to Visual match if possible (Simplified)
        # ... logic for fuzzy matching name ...
        # If we have OCR text but no code match, return it for confirmation
        if full_text.strip():
            return {
                "scan_method": "visual",
                "confidence": 0.6,
                "requires_confirmation": True,
                "card_data": {
                    "name": full_text.split('\n')[0][:50], # Guessing first line is name
                    "game": "Unknown",
                    "set_code": "",
                    "card_number": "",
                    "image_path": s3_url if s3_url else ""
                }
            }

        return {
            "scan_method": "manual",
            "confidence": 0.0,
            "requires_confirmation": True,
            "card_data": None
        }

    def _parse_card_code(self, text):
        # Regex for patterns like LOB-001, SV1-025, EN-023
        # Yu-Gi-Oh!: XXX-ENXXX or XXX-XXX
        # Pokemon: XXX/XXX or XXX-XXX
        patterns = [
            r'([A-Z0-9]+)-([A-Z0-9]+)', # General hyphenated code
            r'([A-Z0-9]+)/([A-Z0-9]+)', # Slash used in some games
            r'([A-Z]{2,3})([0-9]{3})'    # Direct concatenation
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    "set": match.group(1),
                    "number": match.group(2)
                }
        return None
