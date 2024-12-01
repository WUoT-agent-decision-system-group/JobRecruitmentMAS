from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.JobOffer import JobOffer, JobOfferStatus

COLLECTION_NAME = "jobOffers"


class JobOfferRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(JobOffer, db_name, COLLECTION_NAME, logger)

    def change_application_status(self, job_offer_id: str, candidate_ids: list[str],
                                  status: JobOfferStatus) -> bool:
        return self.update(
            job_offer_id,
            {"applications.$[elem].status": status.value},
            [{"elem.candidate_id": {"$in": candidate_ids}}]
        )
