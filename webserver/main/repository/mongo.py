import pymongo

from main.constant import ID
from main.logger.custom_logging import log, log_error
from main.utils.decorators import MeasureTime


@MeasureTime
def collection_insert_one(mongo_collection, entry):
    try:
        mongo_collection.insert_one(entry)
        log(f"Entry inserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entry insertion to collection {mongo_collection.name} failed!")
        return False


@MeasureTime
def collection_upsert_one(mongo_collection, filter_criteria, update_data):
    try:
        mongo_collection.update_one(filter_criteria, update_data, upsert=True)
        log(f"Entry upserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entry upsertion to collection {mongo_collection.name} failed!")
        return False


@MeasureTime
def collection_upsert_many(mongo_collection, filter_criteria_list, update_data_list):
    try:
        mongo_collection.update_many({'$or': filter_criteria_list}, {'$set': update_data_list}, upsert=True)
        log(f"Entries upserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entries upsertion to collection {mongo_collection.name} failed!")
        return False


@MeasureTime
def collection_insert_many(mongo_collection, entries):
    try:
        mongo_collection.insert_many(entries)
        log(f"Entries inserted to collection {mongo_collection.name} successfully!")
        return True
    except:
        log_error(f"Entries insertion to collection {mongo_collection.name} failed!")
        return False


@MeasureTime
def collection_find_all(mongo_collection, query_object, sort_field=None, sort_order=pymongo.ASCENDING,
                        skip=0, limit=10):
    try:
        log(f"Getting entries from collection {mongo_collection.name}")
        catalogue_objects = mongo_collection.find(query_object)
        if sort_field:
            secondary_sort_field, secondary_sort_order = ID, pymongo.ASCENDING
            catalogue_objects = catalogue_objects.sort([(sort_field, sort_order),
                                                        (secondary_sort_field, secondary_sort_order)])
        catalogue_objects = catalogue_objects.skip(skip).limit(limit)
        count = mongo_collection.count_documents(query_object)
        catalogues = [dict(c) for c in catalogue_objects]
        for c in catalogues:
            c.pop('_id')
            c.pop('created_at', None)
        log(f"Got entries from collection {mongo_collection.name} successfully")
        return {'count': count, 'data': catalogues}
    except:
        log_error(f"Getting Entries for collection {mongo_collection.name} failed!")
        return None


@MeasureTime
def collection_find_one(mongo_collection, query_object):
    catalog = mongo_collection.find_one(query_object)
    catalog.pop('_id')
    catalog.pop('created_at', None)
    return catalog


@MeasureTime
def collection_get_count(mongo_collection, query_object):
    count = mongo_collection.count_documents(query_object)
    return count
