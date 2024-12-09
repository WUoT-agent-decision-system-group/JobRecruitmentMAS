from logging import Logger
from typing import List, Optional

from bson.objectid import ObjectId

from app.dataaccess.model.Recruitment import Recruitment
from app.dataaccess.RecruitmentRepository import RecruitmentRepository


class RecruitmentModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruitment_repository = RecruitmentRepository(dbname, self.logger)

    def get(self, _id: str) -> Recruitment:
        return self.__recruitment_repository.get(_id)

    def get_by_job_and_candidate(
        self, job_offer_id: str, candidate_id: str
    ) -> Optional[List[Recruitment]]:
        return self.__recruitment_repository.get_many_by_filter(
            {
                "job_offer_id": ObjectId(job_offer_id),
                "candidate_id": ObjectId(candidate_id),
            }
        )

    def create(self, recruitment: Recruitment) -> str:
        return self.__recruitment_repository.create(recruitment)

    def update(self, _id: str, query: dict) -> bool:
        self.__recruitment_repository.update(_id, {"$set": query})

    def increment(self, _id: str, query: dict) -> None:
        self.__recruitment_repository.update(_id, {"$inc": query})

    def saveRating(self, job_offer_id: str, candidate_id: str, rating: int) -> bool:
        recruitments = self.get_by_job_and_candidate(job_offer_id, candidate_id)

        if len(recruitments) == 0:
            f"No recruitments with job_offer_id: {self.agent.job_offer_id} and candidate_id: {self.agent.candidate_id} found."
            return False
        
        return self.update(recruitments[0]._id, {"application_rating": rating})
