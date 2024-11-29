from logging import Logger

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.utils.configuration import MASConfiguration


class MongoConnector:
    def __init__(self, db_name: str, logger: Logger):
        self.logger = logger
        self.db_name = db_name
        self._client = None
        self.db = None
        self._connect()

    def _connect(self):
        self.logger.info("Connecting to db: %s.", self.db_name)
        config = MASConfiguration.load()
        dbhost = config.db.host
        try:
            self._client = MongoClient(dbhost)
            self.db = self._client[self.db_name]
            self._client.admin.command('ping')
            self.logger.info("Connected to db: %s.", self.db_name)

        except ConnectionFailure:
            self.logger.error("Cannot connect to db %s in %s.",
                              self.db_name, dbhost)
