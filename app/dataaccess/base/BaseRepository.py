from abc import ABC
from logging import Logger
from typing import Generic, Type, TypeVar

from bson.objectid import ObjectId
from pymongo.collection import Any, Collection, Mapping, Sequence

from app.dataaccess.model.BaseObject import BaseObject

from .helpers import map_id, map_ids
from .MongoConnector import mongo_container

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(
        self, obj_class: Type[T], db_name: str, collection_name: str, logger: Logger
    ):
        self.db_name = db_name
        self.logger = logger
        self.obj_class = obj_class
        self.collection_name = collection_name

        client = mongo_container.mongo_connector().client
        self.collection: Collection = client[self.db_name].get_collection(
            collection_name
        )
        self.logger.info(
            "Connected with collection %s in db %s", self.collection_name, self.db_name
        )

    def _doc_to_obj(self, document) -> T:
        return self.obj_class(**document)

    def _docs_to_obj(self, documents: list) -> T:
        return [self._doc_to_obj(doc) for doc in documents]

    def _log_info(self, info: str):
        self.logger.info("[%s] %s", self.collection_name, info)

    def _log_warning(self, warning: str):
        self.logger.warning("[%s] %s", self.collection_name, warning)

    def _log_error(self, error: str):
        self.logger.error("[%s] %s", self.collection_name, error)

    def _log_debug(self, debug: str):
        self.logger.debug("[%s] %s", self.collection_name, debug)

    def create(self, obj: T) -> str:
        try:
            obj: BaseObject = obj
            obj.to_db_format()
            obj_dict = obj.__dict__
            self._log_info(f"Creating object: {obj_dict}.")
            result = self.collection.insert_one(obj_dict)
            _id = str(result.inserted_id)
            self._log_info(f"Created object with id: {_id}.")
            return _id
        except Exception as e:
            self._log_error(e)
            return None

    def get(self, obj_id: str) -> T:
        try:
            self._log_info(f"Get object by id {obj_id} called.")
            result = self.collection.find_one(map_id(obj_id))

            if result:
                self._log_info(f"Get object by id returned {str(result)[:20]}.")
                return self._doc_to_obj(result)

            self._log_warning(f"Object {obj_id} not found.")
            return None
        except Exception as e:
            self._log_error(e)
            return None

    def update(
        self,
        obj_id: str,
        updates: dict,
        array_filters: Sequence[Mapping[str, Any]] = None,
    ) -> bool:
        """
        Updates field in `updates` for `obj_id`.

        Example: update('6749b2b613be3a8fd0943d71',{"name":"qwerty", "email":"123@321.com"})
        """
        try:
            self._log_info(
                f"Update object with id {obj_id} called, updates: {updates}."
            )
            result = self.collection.update_one(
                map_id(obj_id), updates, array_filters=array_filters
            )

            if result.modified_count != 1:
                self._log_warning(
                    f"Update failed (modified {result.modified_count} objects)."
                )
                return False

            self._log_info(f"Update object {obj_id} succeeded.")
            return True
        except Exception as e:
            self._log_error(e)
            return None

    def update_overwrite(self, obj_id: str, obj: T) -> bool:
        """Overrides object of given id. `id` in `obj` should be empty string."""
        try:
            obj_dict = obj.__dict__
            obj_dict.pop("_id")

            self._log_info(
                f"Update (overwrite) object with id {obj_id} called, data: {obj_dict}."
            )
            result = self.collection.update_one(map_id(obj_id), {"$set": obj_dict})
            if result.modified_count != 1:
                self._log_warning(
                    f"Update (overwrite) failed (modified: {result.modified_count})."
                )
                return False

            self._log_info(f"Update (overwrite) object {obj_id} succeeded.")
            return True
        except Exception as e:
            self._log_error(e)
            return None

    def delete(self, obj_id: str) -> bool:
        try:
            self._log_info(f"Delete object {obj_id} called.")
            result = self.collection.delete_one(map_id(obj_id))
            if result.deleted_count != 1:
                self._log_warning(
                    f"Delete {obj_id} failed (deleted: {result.deleted_count})."
                )
                return False

            self._log_info(f"Delete object {obj_id} succeeded.")
            return True
        except Exception as e:
            self._log_error(e)
            return None

    def find_all(self) -> list[T]:
        try:
            self._log_info("Find all called.")
            results = list(self.collection.find({}))
            self._log_info(f"Find all returned {len(results)} objects.")
            return self._docs_to_obj(results)
        except Exception as e:
            self._log_error(e)
            return None

    def get_many_by_ids(self, ids: list[str]) -> list[T]:
        try:
            self._log_info(f"Get objects by ids: {ids} called.")
            object_ids = map_ids(ids)
            documents = list(self.collection.find({"_id": {"$in": object_ids}}))
            self._log_info(f"Get objects by ids returned {len(documents)}.")
            return self._docs_to_obj(documents)
        except Exception as e:
            self._log_error(e)

    def get_many_by_filter(self, query: dict) -> list[T]:
        """Example: get_many_by_filter({"name": "qwerty", "email": "123@321.com"})"""

        try:
            self._log_info(f"Get by filter {query} called.")
            documents = list(self.collection.find(query))
            self._log_info(f"Get by filter {query} returned {len(documents)} objects.")
            return self._docs_to_obj(documents)
        except Exception as e:
            self._log_error(e)
            return None
