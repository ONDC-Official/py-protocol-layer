from enum import Enum


class DatabaseError(Enum):
    OnWriteError = {
        "code": "BAP_006",
        "message": "Error when writing to DB",
    }
    OnReadError = {
        "code": "BAP_007",
        "message": "Error when reading from DB",
    }
    NotFoundError = {
        "code": "BAP_008",
        "message": "No message with the given ID",
    }
    OnDeleteError = {
        "code": "BAP_009",
        "message": "Error when deleting from DB",
    }


class RegistryLookupError(Enum):
    RegistryError = {
        "code": "BAP_001",
        "message": "Error when writing to DB",
    }
    NoSubscribersFoundError = {
        "code": "BAP_002",
        "message": "Error when reading from DB",
    }
