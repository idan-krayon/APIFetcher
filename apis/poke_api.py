import os
from typing import Any, Dict, List

import pydash
from dotenv import load_dotenv

from apis.base_api import CharacterAPI
from models.character import Character, OriginEnum

load_dotenv()


class PokeAPI(CharacterAPI):
    """
    Service class for the Pokémon API
    """

    def __init__(self):
        """
        Initialize the Pokémon API service.
        """
        self.API_URL = os.getenv(
            "POKE_API", "https://pokeapi.co/api/v2/pokemon?limit=1000"
        )
        super().__init__(rate_limit=100)

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch character data from the API.
        :return: List of character data.
        """
        return await self.fetch_paginated_data(self.API_URL)

    async def normalize_data(self, raw_data: List[Dict[str, Any]]) -> list[Character]:
        """
        Normalize the raw data from the API.
        :param raw_data: Raw character data.
        :return: Normalized character data.
        """
        seen = set()
        characters = []
        for item in raw_data:
            name = item["name"].capitalize()
            if name in seen:
                continue

            seen.add(name)

            spec_url = item.get("url", "Unknown")
            spec_details = self.fetcher.details_dict.get(spec_url, {})
            types = pydash.get(spec_details, "types", [])
            types = [pydash.get(t, "type.name", "Unknown") for t in types]

            characters.append(
                Character(
                    name=name,
                    origin=OriginEnum.POKEMON,
                    species=", ".join(types),
                    additional_attributes={
                        "base_experience": item.get("base_experience", 0),
                    },
                )
            )
        return characters
