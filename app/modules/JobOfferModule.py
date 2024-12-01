from logging import Logger

from app.dataaccess.JobOfferRepository import JobOfferRepository
from app.dataaccess.model.JobOffer import (ApplicationStatus, JobOffer,
                                           JobOfferStatus)


class JobOfferModule():
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__job_offers_repository = JobOfferRepository(dbname, self.logger)

    def get_open_job_offers(self) -> list[JobOffer]:
        query = {"status": {"$ne": JobOfferStatus.CLOSED.value}}
        return self.__job_offers_repository.get_many_by_filter(query)

    def get(self, _id: str) -> JobOffer:
        return self.__job_offers_repository.get(_id)

    def change_application_status(self, job_offer_id: str, candidate_ids: list[str],
                                  status: JobOfferStatus) -> bool:
        if len(candidate_ids) == 0:
            return True

        self.logger.info("Changing status for applications from %s for %s. New status: %s",
                         candidate_ids, job_offer_id, status)

        result = self.__job_offers_repository.change_application_status(
            job_offer_id,
            candidate_ids,
            status
        )

        if not result:
            self.logger.error("Update error for applications %s", candidate_ids)

        return result

    def get_new_applications(self, job_offer_id: str):
        self.logger.info("Checking new applications...")
        jobOffer: JobOffer = self.__job_offers_repository.get(job_offer_id)
        new_appl = [x for x in jobOffer.applications
                    if x.status == ApplicationStatus.NEW]
        self.logger.info("Found %d new applications.", len(new_appl))
        return new_appl
