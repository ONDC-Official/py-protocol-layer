import pymongo

from main.models import get_mongo_collection
from main.models.error import DatabaseError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant


def enrich_provider_details_into_items(provider, item):
    provider_details = dict()
    provider_details[constant.ID] = provider.get(constant.ID)
    provider_details[constant.DESCRIPTOR] = provider.get(constant.DESCRIPTOR)
    item[constant.PROVIDER_DETAILS] = provider_details
    return item


def enrich_location_details_into_items(locations, item):
    try:
        location = next(i for i in locations if i[constant.ID] == item.get(constant.LOCATION_ID))
    except:
        location = {}
    item[constant.LOCATION_DETAILS] = location
    return item


def enrich_category_details_into_items(categories, item):
    try:
        category = next(i for i in categories if i[constant.ID] == item.get(constant.CATEGORY_ID))
    except:
        category = {}
    item[constant.CATEGORY_DETAILS] = category
    return item


def enrich_fulfillment_details_into_items(fulfillments, item):
    try:
        fulfillment = next(i for i in fulfillments if i[constant.ID] == item.get(constant.FULFILLMENT_ID))
    except:
        fulfillment = {}
    item[constant.FULFILLMENT_DETAILS] = fulfillment
    return item


def enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, item):
    item[constant.CONTEXT] = context
    item[constant.BPP_DETAILS] = bpp_descriptor
    item[constant.BPP_DETAILS][constant.BPP_ID] = bpp_id
    return item


def cast_price_and_rating_to_float(item):
    if item.get(constant.PRICE) and item[constant.PRICE]['value']:
        item[constant.PRICE]['value'] = float(item[constant.PRICE]['value'])
    if item.get(constant.RATING) and item[constant.RATING]['value']:
        item[constant.RATING]['value'] = float(item[constant.RATING]['value'])
    return item


def flatten_catalog_into_item_entries(catalog, context):
    item_entries = []
    bpp_id = context.get(constant.BPP_ID)
    if bpp_id:
        bpp_descriptor = catalog.get(constant.BPP_DESCRIPTOR)
        bpp_fulfillments = catalog.get(constant.BPP_FULFILLMENTS)
        bpp_categories = catalog.get(constant.BPP_CATEGORIES)
        bpp_providers = catalog.get(constant.BPP_PROVIDERS)

        for p in bpp_providers:
            provider_locations = p.get(constant.LOCATIONS)
            provider_items = p.get(constant.ITEMS)
            [enrich_provider_details_into_items(p, i) for i in provider_items]
            [enrich_location_details_into_items(provider_locations, i) for i in provider_items]
            [enrich_category_details_into_items(bpp_categories, i) for i in provider_items]
            [enrich_fulfillment_details_into_items(bpp_fulfillments, i) for i in provider_items]
            [enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, i) for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            item_entries.extend(provider_items)

    return item_entries


def add_search_catalogues(bpp_response):
    context = bpp_response[constant.CONTEXT]
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    items = flatten_catalog_into_item_entries(catalog, context)

    search_collection = get_mongo_collection('on_search_items')
    is_successful = mongo.collection_insert_many(search_collection, items)
    if is_successful:
        return get_ack_response(ack=True)
    else:
        return get_ack_response(ack=False, error=DatabaseError.ON_WRITE_ERROR.value)


def get_query_object(**kwargs):
    query_object = {"context.message_id": kwargs['message_id']}
    if kwargs['price_min']:
        query_object.update({'price.value': {'$gte': kwargs['price_min']}})
    if kwargs['price_max']:
        query_object.update({'price.value': {'$lte': kwargs['price_max']}})
    if kwargs['rating']:
        query_object.update({'rating.value': {'$gte': kwargs['rating']}})
    if kwargs['provider_id']:
        query_object.update({'provider_details.id': kwargs['provider_id']})
    if kwargs['category_id']:
        query_object.update({'category_id': kwargs['category_id']})
    if kwargs['fulfillment_id']:
        query_object.update({'fulfillment_id': kwargs['fulfillment_id']})
    return query_object


def get_sort_field_and_order(**kwargs):
    if kwargs['sort_field'] == 'price':
        sort_field = 'price.value'
    elif kwargs['sort_field'] == 'rating':
        sort_field = 'rating.value'
    else:
        sort_field = None
    sort_order = pymongo.ASCENDING if kwargs['sort_order'] == 'asc' else pymongo.DESCENDING
    return sort_field, sort_order


def get_catalogues_for_message_id(**kwargs):
    search_collection = get_mongo_collection('on_search_items')
    query_object = get_query_object(**kwargs)
    sort_field, sort_order = get_sort_field_and_order(**kwargs)
    page_number = kwargs['page_number']
    limit = kwargs['limit']
    skip = page_number * limit
    catalogs = mongo.collection_find_all(search_collection, query_object, sort_field, sort_order,
                                         skip=skip, limit=limit)
    return catalogs
