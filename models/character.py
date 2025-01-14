from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class OriginEnum(str, Enum):
    """
    Enum for character origins
    """

    POKEMON = "Pokémon"
    STAR_WARS = "Star Wars"
    RICK_AND_MORTY = "Rick and Morty"


class Character(BaseModel):
    """
    Character model.
    """

    name: str
    origin: OriginEnum
    species: str
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)
