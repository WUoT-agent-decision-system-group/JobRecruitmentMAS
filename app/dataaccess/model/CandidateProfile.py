from bson import ObjectId

from .BaseObject import BaseObject


class CandidateProfile(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        name: str,
        surname: str,
        email: str,
        applied_jobs: list[str | ObjectId]
    ):
        super().__init__(_id)
        self.applied_jobs = [str(x) for x in applied_jobs]
        self.name = name
        self.surname = surname
        self.email = email

    def to_db_format(self):
        super().to_db_format()
        self.applied_jobs = [ObjectId(x) for x in self.applied_jobs]
