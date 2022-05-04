def collection_insert_one(mongo_collection, catalog):
    mongo_collection.insert_one(catalog)
    return {"status": "ACK"}


def collection_find_all(mongo_collection, query_object):
    catalogue_objects = mongo_collection.find(query_object)
    catalogues = [dict(c) for c in catalogue_objects]
    for c in catalogues:
        c.pop('_id')
    return catalogues


def collection_find_one(mongo_collection, query_object):
    catalog = mongo_collection.find_one(query_object)
    catalog.pop('_id')
    return catalog

