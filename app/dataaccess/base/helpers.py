from typing import List, TypeVar

from bson.objectid import ObjectId
from pymongo.collection import Mapping

T = TypeVar('T')


def map_id(obj_id: str) -> Mapping[str, ObjectId]:
    return {"_id": ObjectId(obj_id)}


def map_ids(ids: List[str]) -> List[Mapping[str, ObjectId]]:
    return [ObjectId(obj_id) for obj_id in ids]
