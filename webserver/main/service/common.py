from main.models import get_mongo_collection
from main.models.error import DatabaseError, RegistryLookupError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant


def add_bpp_response(bpp_response, request_type):
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)

    collection_name = get_mongo_collection(request_type)
    is_successful = mongo.collection_insert_one(collection_name, bpp_response)
    if is_successful:
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
    return bpp_response if bpp_response else {"error": DatabaseError.ON_READ_ERROR.value}
