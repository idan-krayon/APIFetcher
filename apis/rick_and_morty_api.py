import os

from typing import List, Dict, Any

from models.character import Character, OriginEnum
from apis.base_api import CharacterAPI

class RickAndMortyAPI(CharacterAPI):

    def __init__(self):
        """
        Initialize the Rick and Morty API service.
        """
        self.API_URL = os.getenv("RICK_AND_MORTY_API") or "https://rickandmortyapi.com/api/character"
        super().__init__(rate_limit=100)

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch character data from the API.
        :return: List of character data.
        """
        return await self.fetch_paginated_data(self.API_URL, data_key="results", next_key="info.next")

    async def normalize_data(self, raw_data: List[Dict[str, Any]]) -> list[Character]:
        """
        Normalize the raw data from the API.
        :param raw_data: Raw character data.
        :return: Normalized character data.
        """
        seen = set()
        characters = []
        for item in raw_data:
            name = item["name"]
            if name in seen:
                continue

            seen.add(name)
            characters.append(Character(
                name=name,
                origin=OriginEnum.RICK_AND_MORTY,
                species=item.get("species", "Unknown"),
                additional_attributes={
                    "status": item.get("status", "Unknown"),
                }
            ))
        return characters