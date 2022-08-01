from main.config import get_config_by_name
from main.models import get_mongo_collection
from main.models.error import DatabaseError, RegistryLookupError
from main.models.subscriber import SubscriberType
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant
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


def bpp_post_call(request_type, **kwargs):
    uri = f"{kwargs['url']}{request_type}"
    payload = kwargs['data']
    return post_on_bg_or_bpp(uri, payload=payload, headers={'Authorization': kwargs['Authorization']})


def fetch_lookup(request_type, subscriber_id=None):
    subscriber_type = SubscriberType.BG.name if request_type == 'search' else SubscriberType.BPP.name
    payload = {"type": subscriber_type, "domain": get_config_by_name('DOMAIN')}
    payload.update(subscriber_id) if subscriber_id else None
    return post_on_bg_or_bpp(get_config_by_name('REGISTRY_BASE_URL'), payload=payload)

