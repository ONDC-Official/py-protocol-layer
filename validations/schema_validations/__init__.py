import pydantic

from config import get_config_by_name
from models.error import BaseError
from utils.ack_utils import get_ack_response
from validations.schema_validations.retail import validate_retail_schema
from validations.schema_validations.logistics import validate_logistics_schema


def validate_request_type(payload, request_type):
    if request_type == payload["context"]["action"]:
        return None
    else:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": f"Context.action doesn't match the route {request_type}!"})


def validate_schema(payload, request_type):
    try:
        if get_config_by_name("TYPE").split("_")[0] == "RETAIL":
            validate_retail_schema(payload, request_type)
        else:
            validate_logistics_schema(payload, request_type)
        return None
    except pydantic.ValidationError as e:
        error_message = str(e)
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error_message})
