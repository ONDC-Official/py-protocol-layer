import json
import os
f = open(f"{os.getcwd()}/schemas/schema.json")
json_schema = json.load(f)


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
