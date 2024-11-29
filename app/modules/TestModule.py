from logging import Logger

from dataaccess.TestRepository import TestRepository


class TestModule():
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.test_repository = None
        self.load_repositories(dbname)
        # TODO wstrzykiwać MongoConnector

    def load_repositories(self, dbname: str):
        self.test_repository = TestRepository(dbname, self.logger)
