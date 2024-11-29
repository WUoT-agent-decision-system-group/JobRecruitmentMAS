from abc import ABC
from logging import Logger
from typing import Generic, List, Type, TypeVar

from pymongo.collection import Collection

from .helpers import map_id, map_ids
from .MongoConnector import mongo_container

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    def __init__(self, obj_class: Type[T], db_name: str, collection_name: str, logger: Logger):
        self.db_name = db_name
        client = mongo_container.mongo_connector().client
        self.collection_name = collection_name
        self.collection: Collection = client[self.db_name].db[collection_name]
        self.logger = logger
        self.obj_class = obj_class

    def doc_to_obj(self, document) -> T:
        return self.obj_class(**document)

    def docs_to_obj(self, documents: List) -> T:
        return [self.doc_to_obj(doc) for doc in documents]

    def create(self, obj: T) -> str:
        obj_dict = obj.__dict__
        result = self.collection.insert_one(obj_dict)
        return str(result.inserted_id)

    def get(self, obj_id: str) -> T:
        result = self.collection.find_one(map_id(obj_id))
        return self.doc_to_obj(result) if result else None

    def update(self, obj_id: str, updates: dict) -> bool:
        """
        Updates field in `updates` for `obj_id`.

        Example: update('6749b2b613be3a8fd0943d71',{"name":"qwerty", "email":"123@321.com"})
        """

        result = self.collection.update_one(map_id(obj_id), {"$set": updates})
        return result.modified_count == 1

    def update_overwrite(self, obj_id: str, obj: T) -> bool:
        """Overrides object of given id. `id` in `obj` should be empty string."""
        obj_dict = obj.__dict__
        obj_dict.pop("_id")
        result = self.collection.update_one(
            map_id(obj_id), {"$set": obj_dict})
        return result.modified_count == 1

    def delete(self, obj_id: str) -> bool:
        result = self.collection.delete_one(map_id(obj_id))
        return result.deleted_count == 1

    def find_all(self) -> List[T]:
        results = self.collection.find({})
        return self.docs_to_obj(results)

    def get_many_by_ids(self, ids: List[str]) -> List[T]:
        object_ids = map_ids(ids)
        documents = self.collection.find({"_id": {"$in": object_ids}})
        return self.docs_to_obj(documents)

    def get_many_by_filter(self, query: dict) -> List[T]:
        """Example: get_many_by_filter({"name": "qwerty", "email": "123@321.com"})"""
        documents = self.collection.find(query)
        return self.docs_to_obj(documents)
