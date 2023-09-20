from datetime import datetime

import pymongo
import json
from main.logger.custom_logging import log
from main.models import get_mongo_collection
from main.models.error import DatabaseError, RegistryLookupError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant
from main.utils.cryptic_utils import create_authorisation_header
from main.utils.lookup_utils import fetch_subscriber_url_from_lookup
from main.utils.webhook_utils import post_count_response_to_client, post_on_bg_or_bpp
from main.utils.logger import get_logger


logger = get_logger()

def add_bpp_response(bpp_response, request_type):
    log(f"Received {request_type} call of {bpp_response['context']['message_id']} "
        f"for {bpp_response['context']['bpp_id']}")
    collection_name = get_mongo_collection(request_type)
    created_at_str = datetime.utcnow().isoformat()
    bpp_response["created_at"] = created_at_str
    is_successful = mongo.collection_insert_one(collection_name, bpp_response)
    if is_successful:
        message_id = bpp_response[constant.CONTEXT]["message_id"]
        post_count_response_to_client(request_type,
                                      {
                                          "messageId": message_id,
                                          "count": 1
                                      })
        return get_ack_response(context=bpp_response[constant.CONTEXT], ack=True)
    else:
        return get_ack_response(context=bpp_response[constant.CONTEXT], ack=False,
                                error=DatabaseError.ON_WRITE_ERROR.value)


def get_query_object(**kwargs):
    query_object = {"context.message_id": kwargs['message_id']}
    return query_object


def get_bpp_response_for_message_id(request_type, **kwargs):
    search_collection = get_mongo_collection(request_type)
    query_object = get_query_object(**kwargs)
    bpp_response = mongo.collection_find_all(search_collection, query_object, sort_field="created_at",
                                             sort_order=pymongo.DESCENDING)
    if bpp_response:
        if bpp_response['count'] > 0:
            return bpp_response['data']
        else:
            return {"error": DatabaseError.NOT_FOUND_ERROR.value}
    else:
        return {"error": DatabaseError.ON_READ_ERROR.value}


def bpp_post_call(request_type, request_payload):
    subscriber_id = request_payload[constant.CONTEXT][constant.BPP_ID]
    bpp_url = request_payload[constant.CONTEXT]["bpp_uri"] if "bpp_uri" in request_payload[constant.CONTEXT]\
        else fetch_subscriber_url_from_lookup(request_type, subscriber_id=subscriber_id)
    bpp_url_with_route = f"{bpp_url}{request_type}" if bpp_url.endswith("/") else f"{bpp_url}/{request_type}"
    auth_header = create_authorisation_header(request_payload)
    dumpedData = json.dumps(request_payload)
    bpp_response = json.loads(dumpedData)
    add_bpp_response(bpp_response,request_type=request_type)
    return post_on_bg_or_bpp(bpp_url_with_route, payload=request_payload, headers={'Authorization': auth_header})


def log_time_difference(requested_payload, reponse ):

    request_timestamp=requested_payload[0]["context"]["timestamp"]
    response_time=reponse[0]["context"]["timestamp"]
    dt1 = datetime.fromisoformat(request_timestamp.replace('Z', '+00:00'))
    dt2 = datetime.fromisoformat(response_time.replace('Z', '+00:00'))
    time_difference = dt2 - dt1
    logger.info(f"transaction_id: {requested_payload[0]['context']['transaction_id']}, action:{requested_payload[0]['context']['action']}time_difference: {time_difference}")
    return time_difference