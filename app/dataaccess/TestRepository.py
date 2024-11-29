from logging import Logger

from .base.BaseRepository import BaseRepository
from .model.TestObject import TestObject

COLLECTION_NAME = "testcollection"


class TestRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(TestObject, db_name, COLLECTION_NAME, logger)
