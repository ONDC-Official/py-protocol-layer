import hashlib
import os
import pathlib
import random
import string
import uuid
from datetime import datetime

from flask_restx import abort
from flask_sqlalchemy import Model

from main.config import Config
from main.logger.custom_logging import log

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

def get_attrs(klass):
    return [k for k in klass.__dict__.keys()
            if not k.startswith('__')
            and not k.endswith('__')]


def update_base_model_with_dictionary(model: Model, column_dict: dict):
    [setattr(model, key, value) for key, value in column_dict.items() if value is not None and key in get_attrs(model)]
    return model


def sanitize_if_signed_url_already_present(signed_url):
    if Config.S3_PRIVATE_BUCKET in signed_url and URL_SPLITTER in signed_url:
        return signed_url.split(URL_SPLITTER)[0].replace(f"https://{Config.S3_PRIVATE_BUCKET}.s3.amazonaws.com/", "")
    return signed_url


def read_sql(sql_name):
    path = str(pathlib.Path(__file__).parent.parent.resolve())
    sql_path = path + os.sep + "sql/redshift/selects"
    return open(sql_path + os.sep + sql_name).read()

if __name__ == '__main__':
    print(password_hash(None))