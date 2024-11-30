from enum import Enum
from typing import List

from bson import ObjectId

from .BaseObject import BaseObject


class ApplicationStatus(Enum):
    NEW = 0
    PROCESSED = 1
    IN_ANALYSIS = 2
    ANALYZED = 3


class ApplicationDetails(BaseObject):
    def __init__(self, _id, candidate_id: str, status: ApplicationStatus):
        super().__init__(_id)
        self.candidate_id = candidate_id
        self.status = status


class JobOfferStatus(Enum):
    NEW = 0
    PROCESSED = 1
    INPROGRESS = 2
    TOCLOSE = 3
    CLOSED = 4


class JobOffer(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        name: str,
        description: str,
        status: JobOfferStatus,
        applications: List[ApplicationDetails]
    ):
        super().__init__(_id)
        self.name = name
        self.description = description
        self.status = status
        self.applications = applications
