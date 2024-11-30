from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.RecruitmentInfo import RecruitmentInfo

COLLECTION_NAME = "recruitment"


class RecruitmentRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(RecruitmentInfo, db_name, COLLECTION_NAME, logger)
