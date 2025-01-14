import json
from typing import List

from models.character import Character
from storage.manager import BaseStorageManager


class FileStorageManager(BaseStorageManager):
    """
    File storage manager for saving character data to a file.
    """

    async def save(
        self, data: List[Character], *args, file_name: str = "characters.json", **kwargs
    ) -> None:
        """
        Save the data to a file.
        :param data: List of Character objects to save.
        :param file_name: Name of the file to save data to.
        """
        with open(file_name, "w") as file:
            json.dump([char.model_dump() for char in data], file, indent=4)
