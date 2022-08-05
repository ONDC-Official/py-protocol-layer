import json
import os

from jsonschema.exceptions import ValidationError

f = open(f"{os.getcwd()}/main/schemas/schema.json")
json_schema = json.load(f)


def transform_json_schema_error(e: ValidationError):
    absolute_path = list(e.absolute_path)
    path_in_str = ""
    for x in absolute_path:
        path_in_str += f"['{x}']" if type(x) == str else f"[{x}]"
    message = e.message
    final_message = f"Validation error: {message} for path: {path_in_str}"
    return final_message


def get_json_schema_for_given_path(path, request_type='post'):
    path_schema = json_schema['paths'][path][request_type]['requestBody']['content']['application/json']['schema']
    path_schema.update(json_schema)
    return path_schema


def get_json_schema_for_response(path, request_type='post', status_code=200):
    path_schema = json_schema['paths'][path][request_type]['responses'][str(status_code)]['content']['application/json']['schema']
    path_schema['title'] = 'Something'
    path_schema.update(json_schema)
    return path_schema


def get_json_schema_for_component(component):
    path_schema = json_schema['components']['schemas'][component]
    path_schema['title'] = component
    path_schema.update(json_schema)
    return path_schema
