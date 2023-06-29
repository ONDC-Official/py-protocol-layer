from datetime import datetime

import pymongo

from main.logger.custom_logging import log
from main.models import get_mongo_collection
from main.models.error import DatabaseError, RegistryLookupError, BaseError
from main.repository import mongo
from main.repository.ack_response import get_ack_response
from main import constant
from main.utils.lookup_utils import fetch_subscriber_url_from_lookup
from main.utils.cryptic_utils import create_authorisation_header
from main.utils.webhook_utils import post_count_response_to_client, post_on_bg_or_bpp, MeasureTime


def enrich_provider_details_into_items(provider, item):
    provider_details = dict()
    provider_details[constant.ID] = provider.get(constant.ID)
    provider_details[constant.DESCRIPTOR] = provider.get(constant.DESCRIPTOR)
    item[constant.PROVIDER_DETAILS] = provider_details
    return item


def enrich_location_details_into_items(locations, item):
    try:
        location = next(i for i in locations if i[constant.ID] == item[constant.ITEM_DETAILS].get(constant.LOCATION_ID))
    except:
        location = {}
    item[constant.LOCATION_DETAILS] = location
    return item


def enrich_category_details_into_items(categories, item):
    try:
        category = next(i for i in categories if i[constant.ID] == item[constant.ITEM_DETAILS].
                        get(constant.CATEGORY_ID))
    except:
        category = {}
    item[constant.CATEGORY_DETAILS] = category
    return item


def enrich_fulfillment_details_into_items(fulfillments, item):
    try:
        fulfillment = next(i for i in fulfillments if i[constant.ID] == item[constant.ITEM_DETAILS].
                           get(constant.FULFILLMENT_ID))
    except:
        fulfillment = {}
    item[constant.FULFILLMENT_DETAILS] = fulfillment
    return item


def enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, item):
    item[constant.CONTEXT] = context
    item[constant.BPP_DETAILS] = bpp_descriptor
    item[constant.BPP_DETAILS][constant.BPP_ID] = bpp_id
    return item


def cast_price_and_rating_to_float(item_obj):
    item = item_obj[constant.ITEM_DETAILS]
    if item.get(constant.PRICE) and item[constant.PRICE].get('value'):
        item[constant.PRICE]['value'] = float(item[constant.PRICE]['value'])
    if item.get(constant.RATING):
        item[constant.RATING] = float(item[constant.RATING])
    return item


def cast_price_and_rating_to_string(item_obj):
    item = item_obj[constant.ITEM_DETAILS]
    if item.get(constant.PRICE) and item[constant.PRICE].get('value'):
        item[constant.PRICE]['value'] = str(item[constant.PRICE]['value'])
    if item.get(constant.RATING):
        item[constant.RATING] = str(item[constant.RATING])
    return item


def cast_provider_category_fulfillment_id_to_string(item):
    if item.get(constant.PROVIDER_DETAILS) and item[constant.PROVIDER_DETAILS].get('id'):
        item[constant.PROVIDER_DETAILS]['id'] = str(item[constant.PROVIDER_DETAILS]['id'])
    if item.get(constant.CATEGORY_ID):
        item[constant.CATEGORY_ID] = str(item[constant.CATEGORY_ID])
    if item.get(constant.FULFILLMENT_ID):
        item[constant.FULFILLMENT_ID] = str(item[constant.FULFILLMENT_ID])
    return item


def enrich_created_at_timestamp_in_item(item):
    item["created_at"] = datetime.utcnow()
    return item


def flatten_catalog_into_item_entries(catalog, context):
    item_entries = []
    bpp_id = context.get(constant.BPP_ID)
    if bpp_id:
        bpp_descriptor = catalog.get(constant.BPP_DESCRIPTOR)
        bpp_fulfillments = catalog.get(constant.BPP_FULFILLMENTS)
        bpp_providers = catalog.get(constant.BPP_PROVIDERS)

        for p in bpp_providers:
            provider_locations = p.pop(constant.LOCATIONS)
            provider_categories = p.pop(constant.CATEGORIES)
            provider_items = p.pop(constant.ITEMS)
            provider_items = [{"item_details": i} for i in provider_items]
            [i.update({"fulfillments": bpp_fulfillments}) for i in provider_items]
            [i.update({"providers": bpp_providers}) for i in provider_items]
            [i.update({"locations": provider_locations}) for i in provider_items]
            [i.update({"categories": provider_categories}) for i in provider_items]
            [enrich_provider_details_into_items(p, i) for i in provider_items]
            [enrich_location_details_into_items(provider_locations, i) for i in provider_items]
            [enrich_category_details_into_items(provider_categories, i) for i in provider_items]
            [enrich_fulfillment_details_into_items(bpp_fulfillments, i) for i in provider_items]
            [enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, i)
             for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            [cast_provider_category_fulfillment_id_to_string(i) for i in provider_items]
            item_entries.extend(provider_items)

    [enrich_created_at_timestamp_in_item(i) for i in item_entries]
    return item_entries


def add_search_catalogues(bpp_response):
    log(f"Received on_search call of {bpp_response['context']['message_id']} for {bpp_response['context']['bpp_id']}")
    context = bpp_response[constant.CONTEXT]
    if constant.MESSAGE not in bpp_response:
        return get_ack_response(context=context, ack=False, error=RegistryLookupError.REGISTRY_ERROR.value)
    catalog = bpp_response[constant.MESSAGE][constant.CATALOG]
    items = flatten_catalog_into_item_entries(catalog, context)

    if len(items) == 0:
        return get_ack_response(context=context, ack=True)
    search_collection = get_mongo_collection('on_search_items')
    is_successful = True

    for i in items:
        # Upsert a single document
        filter_criteria = {"context.bpp_id": i['context']['bpp_id'],
                           "provider_details.id": i['provider_details']['id'],
                           "item_details.id": i['item_details']['id']}
        update_data = {'$set': i}  # Update data to be inserted or updated
        is_successful = is_successful and mongo.collection_upsert_one(search_collection, filter_criteria, update_data)

    if is_successful:
        message_id = bpp_response[constant.CONTEXT]["message_id"]
        post_count_response_to_client("on_search",
                                      {
                                          "messageId": message_id,
                                          "count": mongo.collection_get_count(search_collection,
                                                                              {"context.message_id": message_id}),
                                          "filters": get_filters_out_of_items(items)
                                      })
        return get_ack_response(context=context, ack=True)
    else:
        return get_ack_response(context=context, ack=False, error=DatabaseError.ON_WRITE_ERROR.value)


@MeasureTime
def gateway_search(search_request):
    request_type = 'search'
    gateway_url = fetch_subscriber_url_from_lookup(request_type)
    search_url = f"{gateway_url}{request_type}" if gateway_url.endswith("/") else f"{gateway_url}/{request_type}"
    auth_header = create_authorisation_header(search_request)
    log(f"making request to bg or bpp with {search_request}")
    return post_on_bg_or_bpp(search_url, payload=search_request, headers={'Authorization': auth_header})


def get_query_object(**kwargs):
    query_object = {"context.message_id": kwargs['message_id']}
    if kwargs['price_min'] and kwargs['price_max']:
        query_object.update({'price.value': {'$gte': kwargs['price_min'], '$lte': kwargs['price_max']}})
    elif kwargs['price_min']:
        query_object.update({'price.value': {'$gte': kwargs['price_min']}})
    elif kwargs['price_max']:
        query_object.update({'price.value': {'$lte': kwargs['price_max']}})

    if kwargs['rating']:
        query_object.update({'rating.value': {'$gte': kwargs['rating']}})
    if kwargs['provider_ids']:
        query_object.update({'provider_details.id': {'$in': [x.strip() for x in kwargs['provider_ids']]}})
    if kwargs['category_ids']:
        query_object.update({'category_id': {'$in': [x.strip() for x in kwargs['category_ids']]}})
    if kwargs['fulfillment_ids']:
        query_object.update({'fulfillment_id': {'$in': [x.strip() for x in kwargs['fulfillment_ids']]}})
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
    page_number = kwargs['page_number'] - 1
    limit = kwargs['limit']
    skip = page_number * limit
    catalogs = mongo.collection_find_all(search_collection, query_object, sort_field, sort_order,
                                         skip=skip, limit=limit)
    if catalogs:
        items = catalogs['data']
        catalogs['data'] = [cast_price_and_rating_to_string(i) for i in items]
        return catalogs
    else:
        return {"error": DatabaseError.ON_READ_ERROR.value}


def get_filters_out_of_items(items):
    category_values = [i[constant.CATEGORY_DETAILS] for i in items if 'id' in i[constant.CATEGORY_DETAILS]]
    fulfillment_values = [i[constant.FULFILLMENT_DETAILS] for i in items if 'id' in i[constant.FULFILLMENT_DETAILS]]
    provider_values = [i[constant.PROVIDER_DETAILS] for i in items if 'id' in i[constant.PROVIDER_DETAILS]]
    price_values = [i[constant.ITEM_DETAILS][constant.PRICE]['value'] for i in items]

    categories = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                       for v in category_values}.values())
    fulfillment = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                        for v in fulfillment_values}.values())
    providers = list({v['id']: {'id': v['id'], 'name': v.get('descriptor', {}).get('name')}
                      for v in provider_values}.values())
    min_price = min(price_values)
    max_price = max(price_values)
    return {
        "categories": categories,
        "fulfillment": fulfillment,
        "providers": providers,
        "minPrice": min_price,
        "maxPrice": max_price,
    }


def check_for_quantity_in_items(items):
    flag = True
    for i in items:
        flag = flag and ("quantity" in i) and ('available' in i['quantity']) and ('maximum' in i['quantity'])
    return flag
