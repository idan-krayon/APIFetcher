import asyncio
import os
from typing import Dict, Any, List, Union
from urllib.parse import urlparse

import aiohttp
from async_lru import alru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

stop_after = os.getenv("TENACITY_MIN_BACKOFF") or 5
multiplier = os.getenv("TENACITY_MULTIPLIER") or 1
min_backoff = os.getenv("TENACITY_MIN_BACKOFF") or 2
max_backoff = os.getenv("TENACITY_MAX_BACKOFF") or 10


def is_data_url(url: str) -> bool:
    """
    Check if a URL is a data-fetchable URL (not static like .jpeg, .png, etc.).
    """
    excluded_extensions = {".jpeg", ".jpg", ".png", ".gif", ".svg", ".webp"}
    path = urlparse(url).path
    return not any(path.endswith(ext) for ext in excluded_extensions)


class Fetcher:
    """
    Fetcher class for making safe requests.
    """
    def __init__(self, rate_limit: int = 20):
        """
        Initialize the Fetcher with a rate limit.
        :param rate_limit: Maximum number of concurrent requests.
        """
        self.semaphore = asyncio.Semaphore(rate_limit)

    @retry(stop=stop_after_attempt(stop_after),
           wait=wait_exponential(multiplier=multiplier, min=min_backoff, max=max_backoff))
    @alru_cache(maxsize=1024)
    async def safe_fetch_single(self, url: str) -> Dict[str, Any]:
        """
        Safely fetch data from a single URL with Memcached caching.
        :param url: The URL to fetch.
        :return: JSON response from the URL.
        """
        if not url and not is_data_url(url):
            return {}

        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    print(f"Fetching data from {url}")
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
                except aiohttp.ClientError as e:
                    raise RuntimeError(f"Request failed for {url}: {str(e)}")
                except Exception as e:
                    raise RuntimeError(f"Unexpected error for {url}: {str(e)}")

    async def safe_fetch_many(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Safely fetch data from multiple URLs.
        """
        tasks = [self.safe_fetch_single(url) for url in urls]
        return await asyncio.gather(*tasks)


class GraphFetcher(Fetcher):
    def __init__(self, rate_limit: int = 20):
        """
        Initialize the GraphFetcher.
        """
        self.visited_urls = set()
        self.details_dict = {}
        super().__init__(rate_limit)

    async def traverse_and_fetch(
        self, node: Union[Dict, List, str], base_field: str = ""
    ) -> None:
        """
        Traverse and fetch data from nodes in the graph.
        :param node: Current node to traverse.
        :param base_field: Field key (for debugging or context).
        :return: None
        """
        if not node:
            return

        if isinstance(node, str) and node.startswith("http") and node not in self.visited_urls:
            if not is_data_url(node):
                return

            try:
                self.visited_urls.add(node)
                self.details_dict[node] = await self.safe_fetch_single(node)
            except Exception as e:
                self.details_dict[node] = {"error": str(e)}

        elif isinstance(node, list):
            await asyncio.gather(*(self.traverse_and_fetch(item, base_field) for item in node))

        elif isinstance(node, dict):
            for key, value in node.items():
                await self.traverse_and_fetch(value, base_field=key)

    async def fetch_graph(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Traverse and fetch all data starting from raw_data.
        :param raw_data: Raw input data.
        :return: Dictionary of fetched details.
        """
        tasks = [self.traverse_and_fetch(item) for item in raw_data]
        await asyncio.gather(*tasks)
        return self.details_dict