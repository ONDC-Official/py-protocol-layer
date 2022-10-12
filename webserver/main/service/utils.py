import hashlib
import json
import random
import string
import uuid
from datetime import datetime

from flask import request
from flask_restx import abort
from main.logger.custom_logging import log
from main.repository.ack_response import get_ack_response
from main.utils.cryptic_utils import verify_authorisation_header
from main.utils.lookup_utils import get_bpp_public_key_from_header

URL_SPLITTER = "?"


def get_unique_id(entity_prefix):
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{entity_prefix}_{current_time}_{str(uuid.uuid4())}"


def create_random_number(num_digit=6):
    return "".join([random.choice(string.digits) for i in range(num_digit)])


def create_random_string(num_digit=6):
    return "".join([random.choice(string.ascii_lowercase) for i in range(num_digit)])


def create_random_alpha_numeric_string(num_digit=6):
    return "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(num_digit)])


def create_ever_increasing_random_number(num_digit=6):
    return str(datetime.now().timestamp())[:num_digit]


def password_hash(incoming_password):
    incoming_password = incoming_password or ""
    h = hashlib.md5(incoming_password.encode())
    return h.hexdigest()


def handle_stop_iteration(func):
    def exception_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StopIteration:
            log(f"element not found with {args} and {kwargs}")
            abort(message="Failed while querying and updating SQL server")

    return exception_handler


def validate_auth_header(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        bg_or_bpp_public_key = get_bpp_public_key_from_header(auth_header)
        if verify_authorisation_header(auth_header, request.get_json(), public_key=bg_or_bpp_public_key):
            return func(*args, **kwargs)
        return get_ack_response(ack=False, error={
            "code": "10001",
            "message": "Invalid Signature"
        }), 401

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper
