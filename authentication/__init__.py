from flask import request

from authentication.ondc_authentication import authenticate_ondc_request
from config import get_config_by_name
from utils.ack_utils import get_ack_response


def authenticate(func):
    def wrapper(*args, **kwargs):
        if get_config_by_name("VERIFICATION_ENABLE"):
            resp = authenticate_request(request.data, request.headers)
            if resp is not None:
                return resp, 401

        resp = func(*args, **kwargs)
        if resp is None:
            return get_ack_response(request.get_json()["context"], ack=True), 200
        else:
            return resp

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def authenticate_request(payload_str, headers):
    return authenticate_ondc_request(payload_str, headers)
