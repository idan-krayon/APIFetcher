import os

from dotenv import load_dotenv
from fastapi import FastAPI

from apis.api_aggregator import APIAggregator
from apis.rick_and_morty_api import RickAndMortyAPI
from storage.file_storage import FileStorageManager

load_dotenv()
app = FastAPI()


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.
    """
    return {"message": "Hello Pulse"}


@app.get("/characters")
async def get_characters():
    """
    Get characters from multiple APIs.
    :return: List of characters.
    """
    file_name = os.getenv("FILE_NAME") or "characters.json"
    apis = [RickAndMortyAPI()]  # Play with it
    # apis = [PokeAPI(), SWAPI(), RickAndMortyAPI()]
    aggregator = APIAggregator(apis)
    characters = await aggregator.aggregate_characters()

    file_storage = FileStorageManager()
    await file_storage.save(characters, file_name)
    return [char.model_dump() for char in characters]
