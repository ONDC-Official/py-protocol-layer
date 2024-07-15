import json

from flask import request

from authentication.ondc_authentication import authenticate_ondc_request
from config import get_config_by_name
from services.request_dump import dump_request_payload_with_response


def authenticate(func):
    def wrapper(*args, **kwargs):
        payload = request.get_json()
        action = payload["context"]["action"]
        app_type = get_config_by_name("TYPE").split("_")[-1]
        if app_type == "BAP":
            auth_enable = "on_" in action
        else:
            auth_enable = "on_" not in action

        if auth_enable and get_config_by_name("VERIFICATION_ENABLE"):
            resp = authenticate_request(request.data, request.headers)
            if resp is not None:
                status_code = 401
                dump_request_payload_with_response(payload, dict(request.headers), resp, status_code=status_code)
                return resp, status_code

        return func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def authenticate_request(payload_str, headers):
    return authenticate_ondc_request(payload_str, headers)