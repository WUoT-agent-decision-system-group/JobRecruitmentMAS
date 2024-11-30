from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.JobOffer import JobOffer

COLLECTION_NAME = "jobOffers"


class JobOfferRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(JobOffer, db_name, COLLECTION_NAME, logger)
