from dependency_injector import containers, providers
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.utils.configuration import MASConfiguration
from app.utils.log_config import LogConfig


class MongoConnector:
    def __init__(self):
        self._connect()

    def _connect(self):
        self.logger = LogConfig.get_logger(self.__class__.__name__)
        config = MASConfiguration.load()
        dbhost = config.db.host
        try:
            self.logger.info("Connecting to mongo: %s.", dbhost)
            self._client = MongoClient(dbhost)
            self._client.admin.command('ping')
            self.logger.info("Connected successfully.")

        except ConnectionFailure:
            self.logger.error("Cannot connect to %s.", dbhost)

    @property
    def client(self):
        return self._client


class MongoContainer(containers.DeclarativeContainer):
    mongo_connector = providers.Singleton(MongoConnector)


mongo_container = MongoContainer()
