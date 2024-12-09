from enum import Enum


class MessageType(Enum):
    START_REQUEST = 1
    START_RESPONSE = 2
    STAGE_RESULT = 3
    STAGE_RESULT_ACK = 4
