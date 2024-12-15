from logging import Logger

from app.dataaccess.JobOfferRepository import JobOfferRepository
from app.dataaccess.model.JobOffer import ApplicationStatus, JobOffer, JobOfferStatus


class JobOfferModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__job_offers_repository = JobOfferRepository(dbname, self.logger)

    def find_all(self) -> list[JobOffer]:
        return self.__job_offers_repository.find_all()

    def get(self, _id: str) -> JobOffer:
        return self.__job_offers_repository.get(_id)

    def change_application_status(
        self, job_offer_id: str, candidate_ids: list[str], status: ApplicationStatus
    ) -> bool:
        if len(candidate_ids) == 0:
            return True

        self.logger.info(
            "Changing status for applications from %s for %s. New status: %s",
            candidate_ids,
            job_offer_id,
            status,
        )

        result = self.__job_offers_repository.change_application_status(
            job_offer_id, candidate_ids, status
        )

        if not result:
            self.logger.error("Update error for applications %s", candidate_ids)

        return result
    
    def change_job_offer_status(
        self, job_offer_id: str, status: JobOfferStatus
    ) -> bool:

        self.logger.info("Changing status for job offer %s. New status: %s", job_offer_id, status)

        result = self.__job_offers_repository.change_job_offer_status(job_offer_id, status)

        if not result:
            self.logger.error("Update error for job offer %s", job_offer_id)

        return result

    def get_new_applications(self, job_offer_id: str):
        self.logger.info("Checking new applications...")
        jobOffer: JobOffer = self.__job_offers_repository.get(job_offer_id)
        new_appl = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.NEW
        ]
        self.logger.info("Found %d new applications.", len(new_appl))
        return new_appl
    
    def get_finished_applications(self, job_offer_id: str):
        self.logger.info("Checking finished applications...")
        jobOffer: JobOffer = self.__job_offers_repository.get(job_offer_id)
        finished_appl = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.FINISHED
        ]
        self.logger.info("Found %d finished applications.", len(finished_appl))
        return finished_appl
    
    def get_processed_applications(self, job_offer_id: str):
        self.logger.info("Checking processed applications...")
        jobOffer: JobOffer = self.__job_offers_repository.get(job_offer_id)
        new_appl = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.PROCESSED
        ]
        self.logger.info("Found %d processed applications.", len(new_appl))
        return new_appl

    def update(self, _id: str, query: dict) -> bool:
        return self.__job_offers_repository.update(_id, {"$set": query})