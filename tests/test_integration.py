import unittest

from apis.poke_api import PokeAPI
from apis.rick_and_morty_api import RickAndMortyAPI
from apis.swapi_api import SWAPI
from models.character import Character


class TestSWAPIIntegration(unittest.IsolatedAsyncioTestCase):
    """
    Integration tests for the SWAPI class.

    REAL DATA IS FETCHED FROM THE API. ITS TAKING TIME TO RUN THE TESTS.
    """

    async def test_fetch_and_normalize_data(self):
        """
        Test fetching and normalizing data from SWAPI.
        """
        swapi = SWAPI()

        raw_data = await swapi.fetch_data()

        self.assertIsInstance(raw_data, list)
        self.assertGreater(len(raw_data), 0, "No data fetched from SWAPI.")
        self.assertIn("name", raw_data[0], "Raw data is missing 'name' field.")
        self.assertIn("species", raw_data[0], "Raw data is missing 'species' field.")

        normalized_data = await swapi.normalize_data(raw_data)

        self.assertIsInstance(normalized_data, list)
        self.assertGreater(
            len(normalized_data), 0, "Normalization returned no characters."
        )

        character: Character = normalized_data[0]
        self.assertIsInstance(character, Character)
        self.assertTrue(character.name, "Character name is empty.")
        self.assertEqual(
            character.origin, "Star Wars", "Character origin is incorrect."
        )
        self.assertIsInstance(
            character.species, str, "Character species is not a string."
        )
        self.assertIsInstance(
            character.additional_attributes,
            dict,
            "Additional attributes are not a dictionary.",
        )

    async def test_pokeapi_fetch_and_normalize(self):
        """
        Test fetching and normalizing data from PokeAPI.
        """
        pokeapi = PokeAPI()

        raw_data = await pokeapi.fetch_data()

        self.assertIsInstance(raw_data, list)
        self.assertGreater(len(raw_data), 0, "No data fetched from PokeAPI.")
        self.assertIn("name", raw_data[0], "Raw data is missing 'name' field.")
        self.assertIn("url", raw_data[0], "Raw data is missing 'url' field.")

        normalized_data = await pokeapi.normalize_data(raw_data)

        self.assertIsInstance(normalized_data, list)
        self.assertGreater(
            len(normalized_data), 0, "Normalization returned no characters."
        )

        character: Character = normalized_data[0]
        self.assertIsInstance(character, Character)
        self.assertTrue(character.name, "Character name is empty.")
        self.assertEqual(character.origin, "Pokémon", "Character origin is incorrect.")
        self.assertIsInstance(
            character.species, str, "Character species is not a string."
        )
        self.assertIsInstance(
            character.additional_attributes,
            dict,
            "Additional attributes are not a dictionary.",
        )

    async def test_rick_and_morty_fetch_and_normalize(self):
        """
        Test fetching and normalizing data from Rick and Morty API.
        """
        rick_and_morty_api = RickAndMortyAPI()

        raw_data = await rick_and_morty_api.fetch_data()

        self.assertIsInstance(raw_data, list)
        self.assertGreater(len(raw_data), 0, "No data fetched from Rick and Morty API.")
        self.assertIn("name", raw_data[0], "Raw data is missing 'name' field.")
        self.assertIn("species", raw_data[0], "Raw data is missing 'species' field.")

        normalized_data = await rick_and_morty_api.normalize_data(raw_data)

        self.assertIsInstance(normalized_data, list)
        self.assertGreater(
            len(normalized_data), 0, "Normalization returned no characters."
        )

        character: Character = normalized_data[0]
        self.assertIsInstance(character, Character)
        self.assertTrue(character.name, "Character name is empty.")
        self.assertEqual(
            character.origin, "Rick and Morty", "Character origin is incorrect."
        )
        self.assertIsInstance(
            character.species, str, "Character species is not a string."
        )
        self.assertIsInstance(
            character.additional_attributes,
            dict,
            "Additional attributes are not a dictionary.",
        )
