from logging import Logger
from typing import List

from app.dataaccess.JobOfferRepository import JobOfferRepository
from app.dataaccess.model.JobOffer import JobOffer, JobOfferStatus


class JobOfferModule():
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__job_offers_repository = JobOfferRepository(dbname, self.logger)

    def get_open_job_offers(self) -> List[JobOffer]:
        query = {"status": {"$ne": JobOfferStatus.CLOSED.value}}
        return self.__job_offers_repository.get_many_by_filter(query)

    def get(self, _id: str) -> JobOffer:
        return self.__job_offers_repository.get(_id)
