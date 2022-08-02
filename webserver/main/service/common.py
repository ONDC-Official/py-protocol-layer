from main.models import get_mongo_collection
from main.models.error import DatabaseError, RegistryLookupError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant
from main.utils.cryptic_utils import create_authorisation_header
from main.utils.lookup_utils import fetch_subscriber_url_from_lookup
from main.utils.webhook_utils import post_count_response_to_client, post_on_bg_or_bpp


def add_bpp_response(bpp_response, request_type):
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)

    collection_name = get_mongo_collection(request_type)
    is_successful = mongo.collection_insert_one(collection_name, bpp_response)
    if is_successful:
        message_id = bpp_response[constant.CONTEXT]["message_id"]
        post_count_response_to_client(request_type,
                                      {
                                          "messageId": message_id,
                                          "count": 1
                                      })
        return get_ack_response(ack=True)
    else:
        return get_ack_response(ack=False, error=DatabaseError.ON_WRITE_ERROR.value)


def get_query_object(**kwargs):
    query_object = {"context.message_id": kwargs['message_id']}
    return query_object


def get_bpp_response_for_message_id(request_type, **kwargs):
    search_collection = get_mongo_collection(request_type)
    query_object = get_query_object(**kwargs)
    bpp_response = mongo.collection_find_all(search_collection, query_object)
    if bpp_response:
        if bpp_response['count'] > 0:
            return bpp_response['data']
        else:
            return {"error": DatabaseError.NOT_FOUND_ERROR.value}
    else:
        return {"error": DatabaseError.ON_READ_ERROR.value}


def bpp_post_call(request_type, request_payload):
    subscriber_id = request_payload.get('bpp_id')
    bpp_url = fetch_subscriber_url_from_lookup(request_type, subscriber_id=subscriber_id)
    bpp_url_with_route = f"{bpp_url}{request_type}" if bpp_url.endswith("/") else f"{bpp_url}/{request_type}"
    auth_header = create_authorisation_header(request_payload)
    return post_on_bg_or_bpp(bpp_url_with_route, payload=request_payload, headers={'Authorization': auth_header})


