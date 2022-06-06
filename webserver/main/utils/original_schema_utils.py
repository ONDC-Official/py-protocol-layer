import json
import os

import requests
from bson import json_util
from jsonschema import validate, ValidationError

from main.utils.decorators import check_for_exception

f = open(f"{os.getcwd()}/main/schemas/original_schema.json")
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
    requests.post(os.getenv("WEBHOOK_URL", "https://webhook.site/05bd9e8b-a62e-4dd9-b8e8-f765eeff4a8f"),
                  json=json.loads(json_util.dumps(payload)))
