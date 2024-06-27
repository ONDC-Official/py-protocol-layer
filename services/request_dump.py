from datetime import datetime

from models import get_mongo_collection
from utils import mongo_utils as mongo


def dump_request_payload(action, payload):
    collection = get_mongo_collection('request_dump')
    return mongo.collection_insert_one(collection, {"action": action, "request": payload,
                                                    "created_at": datetime.utcnow()})


def dump_request_payload_with_response(payload, headers, response, status_code):
    collection = get_mongo_collection('request_dump')
    return mongo.collection_insert_one(collection, {"action": payload["context"]["action"], "request": payload,
                                                    "headers": headers,
                                                    "response": response, "status_code": status_code,
                                                    "created_at": datetime.utcnow()})


def update_dumped_request_with_response(object_id, response, status_code):
    collection = get_mongo_collection('request_dump')
    filter_criteria = {"_id": object_id}
    collection.update_one(filter_criteria, {'$set': {"response": response,
                                                     "status_code": status_code,
                                                     "updated_at": datetime.utcnow()}})


def dump_on_search_payload(payload):
    collection = get_mongo_collection('on_search_dump')
    payload["created_at"] = datetime.utcnow()
    payload["status"] = "PENDING"
    return mongo.collection_insert_one(collection, payload)


def get_request_payloads(action, message_id, status_code=None):
    collection = get_mongo_collection('request_dump')
    filter_condn = {"action": action, "request.context.message_id": message_id}
    filter_condn.update({"status_code": status_code}) if status_code else None
    return mongo.collection_find_all(collection, filter_condn, limit=None)

