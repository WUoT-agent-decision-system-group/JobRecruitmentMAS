from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.RecruitmentInstruction import RecruitmentInstruction

COLLECTION_NAME = "recruitmentInstructions"


class RecruitmentInstructionRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(RecruitmentInstruction, db_name, COLLECTION_NAME, logger)
