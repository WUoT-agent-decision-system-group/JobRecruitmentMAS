from enum import Enum

from bson import ObjectId

from .BaseObject import BaseObject


class RecruitmentStageStatus(Enum):
    CREATED = 1
    IN_PROGRESS = 2
    DONE = 3


class RecruitmentStage(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        recruitment_id: str | ObjectId,
        status: int | RecruitmentStageStatus,
    ):
        super().__init__(_id)
        self.recruitment_id = str(recruitment_id)
        self.status = RecruitmentStageStatus(status)

    def to_db_format(self):
        delattr(self, "_id")
