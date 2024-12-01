from logging import Logger

from .base.BaseRepository import BaseRepository
from .base.helpers import map_ids
from .model.CandidateProfile import CandidateProfile

COLLECTION_NAME = "candidates"


class CandidateRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(CandidateProfile, db_name, COLLECTION_NAME, logger)

    def update_applied_jobs(self, candidate_id: str, jobs: list[str]):
        return self.update(
            candidate_id, {"$push": {"applied_jobs": {"$each": map_ids(jobs)}}}
        )
