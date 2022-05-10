from main.models import get_mongo_collection
from main.models.error import DatabaseError
from main.repository import mongo
from main.repository.ack_response import get_ack_response


def add_search_catalogues(search_catalogues):
    search_collection = get_mongo_collection('on_search')
    is_write_successful = mongo.collection_insert_one(search_collection, search_catalogues)
    if is_write_successful:
        return get_ack_response(ack=True)
    else:
        return get_ack_response(ack=False, error=DatabaseError.OnWriteError.value)


def get_catalogues_for_message_id(**kwargs):
    message_id = kwargs['message_id']
    search_collection = get_mongo_collection('on_search')
    query_object = {"context.message_id": message_id}
    catalogs = mongo.collection_find_all(search_collection, query_object)
    return catalogs
