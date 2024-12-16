from logging import Logger

from app.dataaccess.model import Recruiter
from app.dataaccess.RecruiterRepository import RecruiterRepository


class RecruiterModule:
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.__load_repositories(dbname)

    def __load_repositories(self, dbname: str):
        self.__recruiter_repository = RecruiterRepository(dbname, self.logger)

    def get(self, _id: str) -> Recruiter:
        return self.__recruiter_repository.get(_id)
