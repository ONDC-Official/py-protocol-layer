import pymongo


def collection_insert_one(mongo_collection, catalog):
    try:
        mongo_collection.insert_one(catalog)
        return True
    except:
        raise Exception("DatabaseError.OnWriteError")


def collection_find_all(mongo_collection, query_object, sort_field=None, sort_order=pymongo.ASCENDING):
    catalogue_objects = mongo_collection.find(query_object)
    if sort_field:
        catalogue_objects = catalogue_objects.sort(sort_field, sort_order)
    catalogues = [dict(c) for c in catalogue_objects]
    for c in catalogues:
        c.pop('_id')
    return catalogues


def collection_find_one(mongo_collection, query_object):
    catalog = mongo_collection.find_one(query_object)
    catalog.pop('_id')
    return catalog

