from datetime import datetime

import pymongo

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


def get_query_object_for_request_dump(**kwargs):
    query_object = {}
    if kwargs['action']:
        query_object.update({'action': kwargs['action']})
    if kwargs['transaction_id']:
        query_object.update({'request.context.transaction_id': kwargs['transaction_id']})
    if kwargs['message_id']:
        query_object.update({'request.context.message_id': kwargs['message_id']})
    if kwargs['bpp_id']:
        query_object.update({'request.context.bpp_id': kwargs['bpp_id']})
    # if kwargs['provider_id']:
    #     query_object.update({'request.message.bpp/providers.id': kwargs['provider_id']})

    return query_object


def get_request_logs(**kwargs):
    request_dump_collection = get_mongo_collection('request_dump')
    query_object = get_query_object_for_request_dump(**kwargs)
    sort_order = pymongo.ASCENDING if kwargs.get('sort_order') == 'asc' else pymongo.DESCENDING
    page_number = kwargs['page_number'] - 1
    limit = kwargs['limit']
    skip = page_number * limit
    request_dumps = mongo.collection_find_all(request_dump_collection, query_object, "created_at", sort_order,
                                              skip=skip, limit=limit)
    return request_dumps

