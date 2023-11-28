import pymongo

from main.models import get_mongo_collection
from main.repository import mongo


def get_query_object(**kwargs):
    query_object = {}
    if kwargs['transaction_id']:
        query_object.update({'context.transaction_id': kwargs['transaction_id']})
    if kwargs['message_id']:
        query_object.update({'context.message_id': kwargs['message_id']})
    if kwargs['bpp_id']:
        query_object.update({'context.bpp_id': kwargs['bpp_id']})
    if kwargs['domain']:
        query_object.update({'context.domain': kwargs['domain']})
    if kwargs['city']:
        query_object.update({'context.city': kwargs['city']})
    return query_object


def get_on_search_payloads(**kwargs):
    on_search_dump_collection = get_mongo_collection('on_search_dump')
    query_object = get_query_object(**kwargs)
    sort_field, sort_order = 'created_at', pymongo.DESCENDING
    on_search_payloads = mongo.collection_find_all(on_search_dump_collection, query_object, sort_field, sort_order,
                                                   limit=None)['data']
    return on_search_payloads
