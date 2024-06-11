import os

from flask import Flask
from flask_cors import CORS
from flask_rq2 import RQ

import config
from models import init_database
from routes import api

rq: RQ


def create_app(config_name):
    global rq
    flask_app = Flask(__name__)
    flask_app.config.from_object(config.config_by_name[config_name])
    flask_app.app_context().push()
    api.init_app(flask_app)
    rq = RQ(flask_app)
    init_database()
    CORS(flask_app)
    return flask_app
