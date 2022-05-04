import json
from flask import request, g
from pymongo import MongoClient


class JsonObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def initialize_before_calls(app):
    @app.before_request
    def set_page(page=1):
        page = int(request.args.get('page', 1))
        g.page = page


def init_database():
    global mongo_client, mongo_db
    mongo_client = MongoClient('localhost', 27017)
    mongo_db = mongo_client['sandbox_bap']
    print("db_inited")


def get_mongo_collection(collection_name):
    return mongo_db[collection_name]
