import json
from pymongo import MongoClient

from config import get_config_by_name
from logger.custom_logging import log

mongo_client = None
mongo_db = None


class JsonObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def init_database():
    global mongo_client, mongo_db
    if mongo_client is not None and mongo_db is not None:
        return
    else:
        database_url = get_config_by_name('MONGO_DATABASE_URL')
        database_name = get_config_by_name('MONGO_DATABASE_NAME')
        mongo_client = MongoClient(database_url)
        mongo_db = mongo_client[database_name]
        log(f"Mongo client created for {database_url}!")
    create_all_indexes()
    log(f"Created indexes if not already present!")


def create_all_indexes():
    create_ttl_index("request_dump", ttl_in_seconds=get_config_by_name("REQUEST_DUMP_TTL_IN_DAYS")*24*60*60)


def create_ttl_index(collection_name, ttl_in_seconds=None):
    # check if index already exists
    if "created_at_ttl" in get_mongo_collection(collection_name).index_information():
        return
    ttl_in_seconds = ttl_in_seconds if ttl_in_seconds else get_config_by_name('TTL_IN_SECONDS')
    get_mongo_collection(collection_name).create_index("created_at", name="created_at_ttl",
                                                       expireAfterSeconds=ttl_in_seconds)


def get_mongo_collection(collection_name):
    # check if database is initialized
    global mongo_client, mongo_db
    if mongo_client is None or mongo_db is None:
        init_database()
    return mongo_db[collection_name]
