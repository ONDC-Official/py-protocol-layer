from main.models import get_mongo_collection
from main.repository import mongo


def add_search_catalogues(search_catalogues):
    search_collection = get_mongo_collection('on_search')
    mongo.collection_insert_one(search_collection, search_catalogues)
    return {"status": "ACK"}


def get_catalogues_for_message_id(message_id):
    search_collection = get_mongo_collection('on_search')
    query_object = {"context.message_id": message_id}
    return mongo.collection_find_all(search_collection, query_object)
