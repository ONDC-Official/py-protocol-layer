from enum import Enum


class BaseError(Enum):
    CONTEXT_ERROR = "CONTEXT-ERROR"
    CORE_ERROR = "CORE-ERROR"
    DOMAIN_ERROR = "DOMAIN-ERROR"
    POLICY_ERROR = "POLICY-ERROR"
    JSON_SCHEMA_ERROR = "JSON-SCHEMA-ERROR"


class DatabaseError(Enum):
    ON_WRITE_ERROR = {
        "code": "BAP_006",
        "message": "Error when writing to DB",
    }
    ON_READ_ERROR = {
        "code": "BAP_007",
        "message": "Error when reading from DB",
    }
    NOT_FOUND_ERROR = {
        "code": "BAP_008",
        "message": "No message with the given ID",
    }
    ON_DELETE_ERROR = {
        "code": "BAP_009",
        "message": "Error when deleting from DB",
    }


class RegistryLookupError(Enum):
    REGISTRY_ERROR = {
        "code": "BAP_001",
        "message": "Error when writing to DB",
    }
    NO_SUBSCRIBERS_FOUND_ERROR = {
        "code": "BAP_002",
        "message": "Error when reading from DB",
    }
