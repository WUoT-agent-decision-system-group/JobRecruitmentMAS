from abc import ABC

from bson import ObjectId


class BaseObject(ABC):
    def __init__(self, _id: str | ObjectId):
        self._id = str(_id)

    @property
    def id(self):
        return self._id

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)
