from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.Recruiter import Recruiter

COLLECTION_NAME = "recruiters"

class RecruiterRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(Recruiter, db_name, COLLECTION_NAME, logger)
