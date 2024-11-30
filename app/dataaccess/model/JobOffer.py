from enum import Enum

from bson import ObjectId

from .BaseObject import BaseObject, PrintableObject


class ApplicationStatus(Enum):
    NEW = 0
    PROCESSED = 1
    IN_ANALYSIS = 2
    ANALYZED = 3


class ApplicationDetails(PrintableObject):
    def __init__(self, candidate_id: str, status: int | ApplicationStatus):
        self.candidate_id = candidate_id
        self.status = ApplicationStatus(status)


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
        applications: dict
    ):
        super().__init__(_id)
        self.name = name
        self.description = description
        self.status = JobOfferStatus(status)
        self.applications = [ApplicationDetails(**appl) for appl in applications]
