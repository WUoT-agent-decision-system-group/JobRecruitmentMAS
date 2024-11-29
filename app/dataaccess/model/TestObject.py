from bson import ObjectId

from .BaseObject import BaseObject


class TestObject(BaseObject):
    def __init__(self, _id: str | ObjectId, name: str):
        super().__init__(_id)
        self.name = name
