from typing import List

from models.character import Character


class BaseStorageManager:
    """
    Base class for storage managers.
    """

    async def save(self, data: List[Character], *args, **kwargs) -> None:
        """
        Save data to a storage system.
        :param data: List of Character objects to save.
        """
        raise NotImplementedError("The 'save' method must be implemented in subclasses")
