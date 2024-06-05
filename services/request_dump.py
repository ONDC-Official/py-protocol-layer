from datetime import datetime

from models import get_mongo_collection
from utils import mongo_utils as mongo


def dump_request_payload(action, payload):
    collection = get_mongo_collection('request_dump')
    return mongo.collection_insert_one(collection, {"action": action, "request": payload,
                                                    "created_at": datetime.utcnow()})


def update_dumped_request_with_response(object_id, response):
    collection = get_mongo_collection('request_dump')
    filter_criteria = {"_id": object_id}
    collection.update_one(filter_criteria, {'$set': {"response": response,
                                                     "updated_at": datetime.utcnow()}})


def dump_on_search_payload(payload):
    collection = get_mongo_collection('on_search_dump')
    payload["created_at"] = datetime.utcnow()
    payload["status"] = "PENDING"
    return mongo.collection_insert_one(collection, payload)
