from logging import Logger

from bson.objectid import ObjectId

from app.dataaccess.CandidateRepository import CandidateRepository
from app.dataaccess.model.CandidateProfile import CandidateProfile


class CandidateModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__candidate_repository = CandidateRepository(dbname, self.logger)

    def try_add_candidate(self, candidate_to_add: CandidateProfile):
        cand = self.__candidate_repository.get(candidate_to_add.id)
        if cand is None:
            self.logger.info(
                "Candidate %s does not exist yet. Adding...", candidate_to_add.id
            )
            return self.__candidate_repository.create(candidate_to_add) is not None
        else:
            self.logger.info(
                "Candidate %s already exists. Updating...", candidate_to_add.id
            )
            return self.__candidate_repository.update_applied_jobs(
                candidate_to_add.id, candidate_to_add.applied_jobs
            )
