from enum import Enum


class MessageType(Enum):
    START_REQUEST = 1
    START_RESPONSE = 2
    STAGE_RESULT = 3
    STAGE_RESULT_ACK = 4
    ANALYSIS_REQUEST = 5
    ANALYSIS_RESULT = 6
    STATUS_REQUEST = 7
    STATUS_RESPONSE = 8
