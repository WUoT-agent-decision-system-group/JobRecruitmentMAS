from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.RecruitmentStage import RecruitmentStage

COLLECTION_NAME = "recruitmentStages"


class RecruitmentStageRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(RecruitmentStage, db_name, COLLECTION_NAME, logger)
