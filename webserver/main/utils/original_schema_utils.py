import json
import os

import requests
from bson import json_util
from jsonschema import validate, ValidationError

from main.utils.decorators import check_for_exception
from main.utils.path_utils import get_project_root

f = open(f"{get_project_root()}/schemas/original_schema.json")
original_json_schema = json.load(f)


def get_json_schema_for_given_path(path, request_type='post'):
    path_schema = original_json_schema['paths'][path][request_type]['requestBody']['content']['application/json']['schema']
    path_schema.update(original_json_schema)
    return path_schema


def get_json_schema_for_response(path, request_type='post', status_code=200):
    path_schema = original_json_schema['paths'][path][request_type]['responses'][str(status_code)]['content']['application/json']['schema']
    path_schema['title'] = 'Something'
    path_schema.update(original_json_schema)
    return path_schema


def get_json_schema_for_component(component):
    path_schema = original_json_schema['components']['schemas'][component]
    path_schema['title'] = component
    path_schema.update(original_json_schema)
    return path_schema


@check_for_exception
def validate_data_with_original_schema(data, schema_path, passing_in_python_protocol=True):
    try:
        schema = get_json_schema_for_given_path(schema_path)
        validate(data, schema)
    except ValidationError as e:
        validation_webhook(data, str(e), request=schema_path, passing_in_python_protocol=passing_in_python_protocol)


def validation_webhook(data, error, request='on_search', passing_in_python_protocol=True):
    payload = {"request": request, "error": error, "passing_in_python_protocol": passing_in_python_protocol,
               "data": data}
    requests.post(os.getenv("WEBHOOK_URL", "https://webhook.site/d8ab34d4-6fa7-42e5-a7e8-02cd8778c82e"),
                  json=json.loads(json_util.dumps(payload)))
