from logging import Logger

from deprecated import deprecated

from .base.BaseRepository import BaseRepository
from .model.TestObject import TestObject

COLLECTION_NAME = "testcollection"


@deprecated("Obsolete")
class TestRepository(BaseRepository):
    def __init__(self, db_name: str, logger: Logger):
        super().__init__(TestObject, db_name, COLLECTION_NAME, logger)
