import pymongo

from logger.custom_logging import log_error, log


def collection_insert_one(mongo_collection, entry):
    resp = mongo_collection.insert_one(entry)
    return resp.inserted_id


# @MeasureTime
def collection_upsert_one(mongo_collection, filter_criteria, data):
    try:
        if mongo_collection.find_one(filter_criteria):
            filter_criteria.update({"timestamp": {"$lte": data['timestamp']}})
            mongo_collection.update_one(filter_criteria, {'$set': data})
        else:
            mongo_collection.insert_one(data)
        # mongo_collection.update_one(filter_criteria, update_data, upsert=True)
        # log(f"Entry upserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entry upsertion to collection {mongo_collection.name} failed!")
        return False


# @MeasureTime
def collection_upsert_many(mongo_collection, filter_criteria_list, update_data_list):
    try:
        mongo_collection.update_many({'$or': filter_criteria_list}, {'$set': update_data_list}, upsert=True)
        log(f"Entries upserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entries upsertion to collection {mongo_collection.name} failed!")
        return False


# @MeasureTime
def collection_insert_many(mongo_collection, entries):
    try:
        mongo_collection.insert_many(entries)
        log(f"Entries inserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entries insertion to collection {mongo_collection.name} failed!")
        return False


# @MeasureTime
def collection_find_all(mongo_collection, query_object, sort_field=None, sort_order=pymongo.ASCENDING,
                        skip=0, limit=50, geo_spatial=False):
    try:
        log(f"Getting entries from collection {mongo_collection.name}")
        if mongo_collection.name == "on_search_items":
            catalogue_objects = mongo_collection.find(query_object, {"categories": 0, "providers": 0, "locations": 0,
                                                                     "fulfillments": 0})
        else:
            catalogue_objects = mongo_collection.find(query_object)
        if sort_field:
            secondary_sort_field, secondary_sort_order = "id", pymongo.ASCENDING
            catalogue_objects = catalogue_objects.sort([(sort_field, sort_order),
                                                        (secondary_sort_field, secondary_sort_order)])
        if limit:
            catalogue_objects = catalogue_objects.skip(skip).limit(limit)
        else:
            limit = 1
        catalogues = [dict(c) for c in catalogue_objects]
        if geo_spatial:
            count = len(catalogues)
        else:
            count = mongo_collection.count_documents(query_object)
        for c in catalogues:
            c.pop('_id')
            c.pop('created_at', None)
        log(f"Got entries from collection {mongo_collection.name} successfully")
        return {'count': count, 'data': catalogues, "pages": ((count-1)//limit)+1}
    except:
        log_error(f"Getting Entries for collection {mongo_collection.name} failed!")
        return None


# @MeasureTime
def collection_find_distinct(mongo_collection, query_object, distinct=None):
    try:
        log(f"Getting distinct entries from collection {mongo_collection.name}")
        catalogue_objects = mongo_collection.find(query_object)
        if distinct:
            catalogue_objects = catalogue_objects.distinct(distinct)
        return {'count': len(catalogue_objects), 'data': catalogue_objects}
    except:
        log_error(f"Getting Entries for collection {mongo_collection.name} failed!")
        return None


def collection_find_one(mongo_collection, query_object, keep_created_at=False):
    if mongo_collection.name == "on_search_items":
        catalog = mongo_collection.find_one(query_object, {})
    else:
        catalog = mongo_collection.find_one(query_object)
    if catalog:
        catalog.pop('_id')
        if not keep_created_at:
            catalog.pop('created_at', None)
    return catalog


def collection_find_one_with_sort(mongo_collection, query_object, sort_on):
    catalog = mongo_collection.find_one(query_object, sort=[(sort_on, pymongo.DESCENDING)])
    if catalog:
        catalog.pop('_id')
    return catalog

def collection_get_count(mongo_collection, query_object):
    count = mongo_collection.count_documents(query_object)
    return count
