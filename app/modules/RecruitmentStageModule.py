from copy import deepcopy
from logging import Logger
from typing import List, Optional

from bson.objectid import ObjectId

from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.dataaccess.RecruitmentStageRespository import RecruitmentStageRepository


class RecruitmentStageModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_stage_repository = RecruitmentStageRepository(
            dbname, self.logger
        )

    def get(self, _id: str) -> RecruitmentStage:
        return self.__recruitment_stage_repository.get(_id)

    def get_by_recruitment_and_identifier(
        self, recruitment_id: str, identifier: int
    ) -> Optional[List[RecruitmentStage]]:
        return self.__recruitment_stage_repository.get_many_by_filter(
            {"recruitment_id": ObjectId(recruitment_id), "identifier": identifier}
        )

    def create(self, recruitment_stage: RecruitmentStage) -> str:
        recruitment_stage_valued = deepcopy(recruitment_stage)
        recruitment_stage_valued.status = recruitment_stage.status.value
        recruitment_stage_valued.type = recruitment_stage.type.value

        return self.__recruitment_stage_repository.create(recruitment_stage_valued)
