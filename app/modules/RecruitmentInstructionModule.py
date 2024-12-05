from logging import Logger

from app.dataaccess.model.RecruitmentInstruction import RecruitmentInstruction
from app.dataaccess.RecruitmentInstructionRepository import (
    RecruitmentInstructionRepository,
)


class RecruitmentStageModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_stage_repository = RecruitmentInstructionRepository(
            dbname, self.logger
        )

    def get(self, _id: str) -> RecruitmentInstruction:
        return self.__recruitment_stage_repository.get(_id)
