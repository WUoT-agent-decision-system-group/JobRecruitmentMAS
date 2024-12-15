from enum import Enum

from bson import ObjectId

from .BaseObject import BaseObject, PrintableObject


class ApplicationStatus(Enum):
    NEW = 0
    PROCESSED = 1
    IN_ANALYSIS = 2
    ANALYZED = 3
    FINISHED = 4
    REJECTED = 5


class ApplicationDetails(PrintableObject):
    def __init__(
        self,
        candidateId: str | ObjectId,
        status: int | ApplicationStatus,
        name: str,
        surname: str,
        email: str,
        cv: str | ObjectId,
    ):
        self.candidate_id = str(candidateId)
        self.status = ApplicationStatus(status)
        self.name = name
        self.surname = surname
        self.email = email
        self.cv = str(cv)


class JobOfferStatus(Enum):
    NEW = 0
    PROCESSED = 1
    INPROGRESS = 2
    CLOSED = 3


class JobOffer(BaseObject):
    def __init__(
        self,
        _id: str | ObjectId,
        name: str,
        description: str,
        status: JobOfferStatus,
        applications: dict,
        recruiter_id: str | ObjectId,
        best_candidate_id: str | ObjectId,
        max_number_of_candidates: int
    ):
        super().__init__(_id)
        self.name = name
        self.description = description
        self.status = JobOfferStatus(status)
        self.applications = [ApplicationDetails(**appl) for appl in applications]
        self.recruiter_id = recruiter_id
        self.best_candidate_id = best_candidate_id 
        self.max_number_of_candidates = max_number_of_candidates
