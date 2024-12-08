from bson import ObjectId

from .BaseObject import BaseObject


class Recruitment(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        job_offer_id: str | ObjectId,
        candidate_id: str | ObjectId,
        current_priority: int,
    ):
        super().__init__(_id)
        self.job_offer_id = str(job_offer_id)
        self.candidate_id = str(candidate_id)
        self.current_priority = current_priority

    def to_db_format(self):
        delattr(self, "_id")
        self.job_offer_id = ObjectId(self.job_offer_id)
        self.candidate_id = ObjectId(self.candidate_id)
