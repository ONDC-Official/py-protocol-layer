import copy
import hashlib
import json
import re
import random
import string
import uuid
from datetime import datetime
from dateutil import parser

from main import constant
from main.config import get_config_by_name
from main.logger.custom_logging import log
from main.models import get_mongo_collection
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main.utils.cryptic_utils import verify_authorisation_header
from main.utils.lookup_utils import get_bpp_public_key_from_header
from main.utils.webhook_utils import make_request_to_no_dashboard

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
    from flask import abort

    def exception_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StopIteration:
            log(f"element not found with {args} and {kwargs}")
            abort(message="Failed while querying and updating SQL server")

    return exception_handler


def dump_auth_failure_request(auth_header, payload_str, context, public_key):
    collection = get_mongo_collection('auth_failure_request_dump')
    return mongo.collection_insert_one(collection, {"context": context,
                                                    "payload_str": payload_str,
                                                    "auth_header": auth_header,
                                                    "created_at": datetime.utcnow(),
                                                    "public_key": public_key})


def dump_validation_failure_request(payload, error):
    collection = get_mongo_collection('validation_failure_request_dump')
    return mongo.collection_insert_one(collection, {"request": payload,
                                                    "created_at": datetime.utcnow(),
                                                    "error": error})


def dump_all_request(coming_request):
    all_request = copy.deepcopy(coming_request)
    collection = get_mongo_collection('all_request_dump')
    all_request["created_at"] = datetime.utcnow()
    all_request["action"] = all_request.get("context", {}).get("action")
    return mongo.collection_insert_one(collection, all_request)


def validate_auth_header(func):
    from flask import request

    def wrapper(*args, **kwargs):
        dump_all_request(request.get_json()) if get_config_by_name("DUMP_ALL_REQUESTS") else None
        make_request_to_no_dashboard(request.get_json())
        if get_config_by_name("VERIFICATION_ENABLE"):
            auth_header = request.headers.get('Authorization')
            domain = request.get_json().get("context", {}).get("domain")
            public_key = get_bpp_public_key_from_header(auth_header, domain) if auth_header else None

            if public_key and verify_authorisation_header(auth_header, request.data.decode("utf-8"),
                                                          public_key=public_key):
                return func(*args, **kwargs)
            context = json.loads(request.data)[constant.CONTEXT]
            dump_auth_failure_request(auth_header, request.data.decode("utf-8"), context, public_key)
            resp, status_code = get_ack_response(context=context, ack=False, error={
                "code": "10001",
                "message": "Invalid Signature"
            }), 401
            make_request_to_no_dashboard(resp, response=True)
            return resp, status_code
        else:
            resp, status_code = func(*args, **kwargs)
            log("Got success for ondc request, now making call NO dashboard for response")
            make_request_to_no_dashboard(resp, response=True)
            return resp, status_code

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def calculate_duration_ms(iso8601dur: str):
    match = re.match(r'^PT(\d{0,2})([H|S])$', iso8601dur)
    if match:
    # multiply the value by 3600000 if H else 1000 
        return int(match.group(1)) * ((60 * 60 * 1000) if match.group(2) == 'H' else 1000)
    else:
        raise Exception('Duration Error: either empty or not correct format')

def is_on_issue_deadine(duration: float, start_datetime_str: str):
    time_elapsed = datetime.now().timestamp() * 1000 - parser.isoparse(start_datetime_str).timestamp() * 1000
    return duration - time_elapsed < 0