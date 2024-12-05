from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.Recruitment import Recruitment

COLLECTION_NAME = "recruitments"


class RecruitmentRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(Recruitment, db_name, COLLECTION_NAME, logger)
