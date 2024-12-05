from enum import Enum

from bson import ObjectId

from .BaseObject import BaseObject


class StageType(Enum):
    TECHNICAL = 1
    CODE = 2
    LANGUAGE = 3


class RecruitmentInstruction(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        job_offer_id: str | ObjectId,
        stage_number: int,
        stage_types: list[int],
        stage_priorities: list[int],
    ):
        super().__init__(_id)
        self.job_offer_id = str(job_offer_id)
        self.stages_number = stage_number
        self.stage_types = [StageType(st) for st in stage_types]
        self.stage_priorities = [sp for sp in stage_priorities]
