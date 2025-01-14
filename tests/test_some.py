import unittest
from unittest.mock import AsyncMock, patch

from api_helpers.fetcher import GraphFetcher
from apis.api_aggregator import APIAggregator
from apis.base_api import CharacterAPI
from models.character import Character, OriginEnum


class MockAPI(CharacterAPI):
    """
    Mock API for testing.
    """

    async def fetch_data(self):
        return [
            {
                "name": "Luke Skywalker",
                "species": ["https://swapi.dev/api/species/1/"],
                "birth_year": "19BBY",
            },
            {
                "name": "Darth Vader",
                "species": ["https://swapi.dev/api/species/2/"],
                "birth_year": "41.9BBY",
            },
        ]

    async def normalize_data(self, raw_data):
        return [
            Character(
                name=item["name"],
                origin=OriginEnum.STAR_WARS,
                species=", ".join(item.get("species", ["Unknown"])),
                additional_attributes={"birth_year": item["birth_year"]},
            )
            for item in raw_data
        ]


class TestGraphFetcher(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for GraphFetcher class.
    """

    @patch("api_helpers.fetcher.GraphFetcher.safe_fetch_single", new_callable=AsyncMock)
    async def test_fetch_graph(self, mock_fetch):
        mock_fetch.return_value = {"name": "Human"}
        graph_fetcher = GraphFetcher(rate_limit=5)

        raw_data = [{"species": ["https://swapi.dev/api/species/1/"]}]
        result = await graph_fetcher.fetch_graph(raw_data)

        self.assertIn("https://swapi.dev/api/species/1/", result)
        self.assertEqual(result["https://swapi.dev/api/species/1/"], {"name": "Human"})

    @patch("api_helpers.fetcher.GraphFetcher.safe_fetch_single", new_callable=AsyncMock)
    async def test_fetch_graph_with_inner_urls(self, mock_fetch):
        mock_fetch.side_effect = lambda url: {
            "https://swapi.dev/api/species/1/": {
                "name": "Human",
                "related": "https://swapi.dev/api/related/1/",
            },
            "https://swapi.dev/api/related/1/": {"name": "Related Species"},
        }.get(url, {"error": "Not Found"})

        graph_fetcher = GraphFetcher(rate_limit=5, enable_recursive_fetch=True)

        raw_data = [{"species": ["https://swapi.dev/api/species/1/"]}]
        result = await graph_fetcher.fetch_graph(raw_data)

        self.assertIn("https://swapi.dev/api/species/1/", result)
        self.assertEqual(result["https://swapi.dev/api/species/1/"]["name"], "Human")
        self.assertIn("https://swapi.dev/api/related/1/", result)
        self.assertEqual(
            result["https://swapi.dev/api/related/1/"]["name"], "Related Species"
        )

    async def test_aggregate_characters(self):
        mock_api1 = MockAPI()
        mock_api2 = MockAPI()
        aggregator = APIAggregator([mock_api1, mock_api2])

        characters = await aggregator.aggregate_characters()

        self.assertEqual(len(characters), 2)  # Only unique names
        self.assertTrue(any(char.name == "Luke Skywalker" for char in characters))
        self.assertTrue(any(char.name == "Darth Vader" for char in characters))

    async def test_aggregate_characters_with_different_attributes(self):
        mock_api1 = MockAPI()
        mock_api1.fetch_data = AsyncMock(
            return_value=[
                {"name": "Luke Skywalker", "species": ["Human"], "birth_year": "19BBY"},
            ]
        )
        mock_api1.normalize_data = AsyncMock(
            return_value=[
                Character(
                    name="Luke Skywalker",
                    origin=OriginEnum.STAR_WARS,
                    species="Human",
                    additional_attributes={"birth_year": "19BBY"},
                )
            ]
        )

        mock_api2 = MockAPI()
        mock_api2.fetch_data = AsyncMock(
            return_value=[
                {"name": "Luke Skywalker", "species": ["Jedi"], "height": "172"},
            ]
        )
        mock_api2.normalize_data = AsyncMock(
            return_value=[
                Character(
                    name="Luke Skywalker",
                    origin=OriginEnum.STAR_WARS,
                    species="Jedi",
                    additional_attributes={"height": "172"},
                )
            ]
        )

        aggregator = APIAggregator([mock_api1, mock_api2])
        characters = await aggregator.aggregate_characters()

        self.assertEqual(len(characters), 1)
        luke = characters[0]
        self.assertEqual(luke.name, "Luke Skywalker")
        self.assertEqual(luke.species, "Human, Jedi")
        self.assertIn("birth_year", luke.additional_attributes)
        self.assertIn("height", luke.additional_attributes)
        self.assertEqual(luke.additional_attributes["birth_year"], "19BBY")
        self.assertEqual(luke.additional_attributes["height"], "172")
