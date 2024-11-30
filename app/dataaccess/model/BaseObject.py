from abc import ABC

from bson import ObjectId


class PrintableObject(ABC):
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


class BaseObject(PrintableObject):
    def __init__(self, _id: str | ObjectId):
        self._id = str(_id)

    @property
    def id(self):
        return self._id
