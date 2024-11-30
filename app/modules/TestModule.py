from logging import Logger

from deprecated import deprecated

from app.dataaccess.TestRepository import TestRepository


@deprecated("Obsolete")
class TestModule():
    def __init__(self, dbname: str, logger: Logger):
        self.logger = logger
        self.load_repositories(dbname)

    def load_repositories(self, dbname: str):
        self.test_repository = TestRepository(dbname, self.logger)
