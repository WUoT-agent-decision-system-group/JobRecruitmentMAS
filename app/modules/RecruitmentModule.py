from logging import Logger

from bson.objectid import ObjectId

from app.dataaccess.model.RecruitmentInfo import RecruitmentInfo
from app.dataaccess.RecruitmentRepository import RecruitmentRepository


class RecruitmentModule():
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_repository = RecruitmentRepository(dbname, self.logger)

    def get_stages_info(self, job_offer_id) -> RecruitmentInfo:
        query = {"job_offer_id": ObjectId(job_offer_id)}
        data = self.__recruitment_repository.get_many_by_filter(query)
        if len(data) != 1:
            self.logger.error(f"Invalid number of recruitment info for {job_offer_id}."
                              + f"Found {len(data)}, expected: 1")
            return None
        return data[0]
