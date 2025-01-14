from typing import List, Dict, Any

import pydash
from fastapi import HTTPException

from api_helpers.fetcher import GraphFetcher


class CharacterAPI:
    """
    Base class for character API services
    """

    def __init__(self, rate_limit: int = 20):
        """
        Initialize the character API service.
        """
        self.fetcher = GraphFetcher(rate_limit)

        #self.fetcher = Fetcher(rate_limit)

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch character data from the API.
        :return: List of character data.
        """
        raise NotImplementedError("fetch_data must be implemented by subclasses")

    async def normalize_data(self, raw_data: List[Dict[str, Any]]) -> list["Character"]:
        """
        Normalize the raw data from the API.
        :param raw_data: Raw character data.
        :return: Normalized character data.
        """
        raise NotImplementedError("normalize_data must be implemented by subclasses")

    async def fetch_paginated_data(self, url: str, data_key: str = "results", next_key: str = "next") -> List[
        Dict[str, Any]]:
        """
        Fetch paginated data from an API.
        """
        data = []
        next_url = url

        while next_url:
            response = await self.fetcher.safe_fetch_single(next_url)

            if not response:
                raise HTTPException(status_code=500, detail=f"No response received for URL: {next_url}")

            data.extend(pydash.get(response, data_key, []))
            next_url = pydash.get(response, next_key, None)

        # Enrich the data with details
        await self.fetcher.fetch_graph(data)
        return data
