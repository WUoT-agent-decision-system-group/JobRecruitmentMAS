from bson import ObjectId

from .BaseObject import BaseObject


class RecruitmentStageInfo:
    pass  # TODO


class RecruitmentInfo(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        job_offer: str | ObjectId,
        stages: list[RecruitmentStageInfo],
    ):
        super().__init__(_id)
        self.job_offer = str(job_offer)
        self.stages = stages
