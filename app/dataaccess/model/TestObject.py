from bson import ObjectId
from deprecated import deprecated

from .BaseObject import BaseObject


@deprecated("Obsolete")
class TestObject(BaseObject):
    def __init__(self, _id: str | ObjectId, name: str):
        super().__init__(_id)
        self.name = name
