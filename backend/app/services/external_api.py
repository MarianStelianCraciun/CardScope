import httpx
import logging

logger = logging.getLogger(__name__)

class ExternalCardAPI:
    def __init__(self):
        self.yugioh_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        self.pokemon_url = "https://api.pokemontcg.io/v2/cards"

    async def get_card_details(self, game: str, set_code: str, card_number: str):
        if game.lower() == "yu-gi-oh!":
            return await self._get_yugioh_details(set_code, card_number)
        elif game.lower() == "pokemon":
            return await self._get_pokemon_details(set_code, card_number)
        return None

    async def _get_yugioh_details(self, set_code: str, card_number: str):
        # YGOPRODeck uses cardsetcode (e.g., LOB-001)
        full_code = f"{set_code}-{card_number}"
        params = {"cardset": full_code}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.yugioh_url, params=params)
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    if data:
                        card = data[0]
                        # Extract price and rarity from the matching set if possible
                        price = "0.00"
                        rarity = "Common"
                        
                        full_code = f"{set_code}-{card_number}".upper()
                        sets = card.get("card_sets", [])
                        matching_set = next((s for s in sets if s.get("set_code") == full_code), None)
                        
                        if matching_set:
                            price = matching_set.get("set_price", "0.00")
                            rarity = matching_set.get("set_rarity", "Common")
                        elif card.get("card_prices"):
                            # Fallback to general TCGPlayer price if set matching fails
                            price = card["card_prices"][0].get("tcgplayer_price", "0.00")
                            if sets:
                                rarity = sets[0].get("set_rarity", "Common")
                        
                        return {
                            "name": card.get("name"),
                            "description": card.get("desc"),
                            "price": price,
                            "image_url": card.get("card_images", [{}])[0].get("image_url"),
                            "rarity": rarity
                        }
        except Exception as e:
            logger.error(f"Error fetching Yu-Gi-Oh! data: {e}")
        return None

    async def _get_pokemon_details(self, set_code: str, card_number: str):
        # Pokemon TCG API uses query like 'set.id:sv1 number:25'
        # Note: set_code might need mapping if it doesn't match API's set.id
        query = f"number:{card_number}"
        if set_code:
            query += f" set.id:{set_code.lower()}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.pokemon_url, params={"q": query})
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    if data:
                        card = data[0]
                        price = "0.00"
                        if card.get("tcgplayer", {}).get("prices"):
                            # Get a price, e.g., holofoil market price
                            prices = card["tcgplayer"]["prices"]
                            first_type = list(prices.keys())[0]
                            price = prices[first_type].get("market", "0.00")
                        
                        return {
                            "name": card.get("name"),
                            "description": card.get("flavorText", ""),
                            "price": str(price),
                            "image_url": card.get("images", {}).get("large"),
                            "rarity": card.get("rarity")
                        }
        except Exception as e:
            logger.error(f"Error fetching Pokemon data: {e}")
        return None
