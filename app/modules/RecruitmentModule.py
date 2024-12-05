from logging import Logger
from typing import List

from bson.objectid import ObjectId

from app.dataaccess.model.Recruitment import Recruitment, RecruitmentStageInfo
from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.dataaccess.RecruitmentRepository import RecruitmentRepository


class RecruitmentModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_repository = RecruitmentRepository(dbname, self.logger)

    # def get_stages_info(self, job_offer_id) -> Recruitment:
    #     query = {"job_offer_id": ObjectId(job_offer_id)}
    #     data = self.__recruitment_repository.get_many_by_filter(query)
    #     if len(data) != 1:
    #         self.logger.error(
    #             f"Invalid number of recruitment info for {job_offer_id}."
    #             + f"Found {len(data)}, expected: 1"
    #         )
    #         return None
    #     return data[0]

    def get(self, _id: str) -> Recruitment:
        return self.__recruitment_repository.get(_id)

    def create(self, recruitment: Recruitment) -> str:
        return self.__recruitment_repository.create(recruitment)

    def update_stages(
        self, recruitment: Recruitment, recruitment_stages: List[RecruitmentStage]
    ):
        recruitment_stages_info = list(
            map(lambda rs: RecruitmentStageInfo(rs._id), recruitment_stages)
        )
        recruitment.stages.extend(recruitment_stages_info)

        recruitment_stages_info = list(
            map(lambda rsi: rsi.__dict__, recruitment_stages_info)
        )
        self.__recruitment_repository.update(
            recruitment._id, {"$push": {"stages": {"$each": recruitment_stages_info}}}
        )

        self.logger.info(
            f"Updated stages array for recruitment with id: {recruitment._id}"
        )
