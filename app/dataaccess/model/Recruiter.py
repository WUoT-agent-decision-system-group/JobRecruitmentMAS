from bson import ObjectId

from .BaseObject import BaseObject

class Recruiter(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        name: str,
        surname: str
    ):
        super().__init__(_id)
        self.name = name
        self.surname = surname