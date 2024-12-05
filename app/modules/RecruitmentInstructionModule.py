from logging import Logger

from bson import ObjectId

from app.dataaccess.model.RecruitmentInstruction import RecruitmentInstruction
from app.dataaccess.RecruitmentInstructionRepository import (
    RecruitmentInstructionRepository,
)


class RecruitmentInstructionModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_stage_repository = RecruitmentInstructionRepository(
            dbname, self.logger
        )

    def get_by_job_offer_id(self, job_offer_id: str) -> RecruitmentInstruction:
        return self.__recruitment_stage_repository.get_many_by_filter(
            {"job_offer_id": ObjectId(job_offer_id)}
        )[0]
