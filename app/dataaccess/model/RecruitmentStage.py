from enum import Enum

from bson import ObjectId

from .BaseObject import BaseObject
from .RecruitmentInstruction import StageType


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
        type: int | StageType,
        priority: int,
    ):
        super().__init__(_id)
        self.recruitment_id = str(recruitment_id)
        self.status = RecruitmentStageStatus(status)
        self.type = StageType(type)
        self.priority = priority

    def to_db_format(self):
        delattr(self, "_id")
        self.recruitment_id = ObjectId(self.recruitment_id)
