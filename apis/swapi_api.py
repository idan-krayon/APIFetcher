import os
from typing import Any, Dict, List

from dotenv import load_dotenv

from apis.base_api import CharacterAPI
from models.character import Character, OriginEnum

load_dotenv()


class SWAPI(CharacterAPI):
    """
    Service class for the Star Wars API
    """

    def __init__(self):
        """
        Initialize the Star Wars API service.
        """
        self.API_URL = os.getenv("SWAPI_API", "https://swapi.dev/api/people/")
        super().__init__(rate_limit=100)

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch character data from the API.
        :return: List of character data.
        """
        return await self.fetch_paginated_data(
            self.API_URL, data_key="results", next_key="next"
        )

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

            species = item.get("species", ["Unknown"])
            species = [
                self.fetcher.details_dict.get(spec, {}).get("name", spec)
                for spec in species
            ]

            seen.add(name)
            characters.append(
                Character(
                    name=name,
                    origin=OriginEnum.STAR_WARS,
                    species=", ".join(species),
                    additional_attributes={
                        "birth_year": item.get("birth_year", "Unknown"),
                        # Example of a new attribute
                        # "height": item.get("height", "Unknown"),
                    },
                )
            )
        return characters
