from functools import wraps

from flask import request

from utils.ack_utils import get_ack_response
from validations.business_rule_validations import validate_business_rules
from validations.schema_validations import validate_schema, validate_request_type


def validate_payload(request_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resp = validate_ondc_request(request_type, request.get_json(), request.headers)
            if resp is not None:
                return resp, 400

            func(*args, **kwargs)
            return get_ack_response(request.get_json()["context"], ack=True), 200

        return wrapper
    return decorator


def validate_ondc_request(request_type, payload, headers):
    request_type_validation_resp = validate_request_type(payload, request_type)
    if request_type_validation_resp is None:
        request_type = payload["context"]["action"]
        if request_type == "on_search":
            full_or_inc = headers.get("X-ONDC-Search-Response", "full")
            request_type = f"{full_or_inc}_{request_type}"

        schema_validation_resp = validate_schema(payload, request_type)
        if schema_validation_resp is None:
            return validate_business_rules(payload, request_type)
        else:
            return schema_validation_resp
    else:
        return request_type_validation_resp
