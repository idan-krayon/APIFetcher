import asyncio
from typing import List, Dict

from apis.base_api import CharacterAPI
from models.character import Character


class APIAggregator:
    """
    Aggregates data from multiple APIs.
    """

    def __init__(self, apis: List[CharacterAPI]):
        """
        Initialize the character aggregator with a list of APIs.
        :param apis: List of character APIs.
        """
        self.apis = apis

    async def aggregate_characters(self) -> List[Character]:
        """
        Aggregate characters from multiple APIs.
        :return: List of normalized and merged characters.
        """
        all_characters = {}
        tasks = [api.fetch_data() for api in self.apis]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for api, raw_data in zip(self.apis, results):
            if isinstance(raw_data, Exception):
                continue

            normalized_data = await api.normalize_data(raw_data)
            self._merge_characters(all_characters, normalized_data)

        return sorted(all_characters.values(), key=lambda x: x.name.lower())

    def _merge_characters(self, character_map: Dict[str, Character], new_characters: List[Character]) -> None:
        """
        Merge a list of new characters into an existing character map.
        :param character_map: Existing map of characters, keyed by name.
        :param new_characters: New characters to merge.
        """
        for new_char in new_characters:
            if new_char.name in character_map:
                existing_char = character_map[new_char.name]
                existing_char.species = self._merge_lists(existing_char.species.split(", "), new_char.species.split(
                    ", "))  # just an example for one of the fields e.g; species
                existing_char.additional_attributes.update(new_char.additional_attributes)
            else:
                character_map[new_char.name] = new_char

    @staticmethod
    def _merge_lists(list1: List[str], list2: List[str]) -> str:
        """
        Merge two lists of strings, removing duplicates and preserving order.
        :param list1: First list.
        :param list2: Second list.
        :return: Comma-separated string of merged values.
        """
        merged = list(dict.fromkeys(list1 + list2))
        return ", ".join(merged)
