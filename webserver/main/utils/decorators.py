import traceback

from flask import request
from flask_expects_json import expects_json
from flask_restx import abort

from main.utils.cryptic_utils import verify_authorisation_header
from main.utils.lookup_utils import get_bpp_public_key_from_header


def expects_json_handling_validation(*args, **kwargs):
    try:
        return expects_json(*args, **kwargs)
    except:
        print("comig here")


def check_for_exception(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    return _wrapper


def validate_auth_header(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        bg_or_bpp_public_key = get_bpp_public_key_from_header(auth_header)
        if verify_authorisation_header(auth_header, request.get_json(), public_key=bg_or_bpp_public_key):
            return func(*args, **kwargs)
        abort(403, message="Unauthorized!")

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

