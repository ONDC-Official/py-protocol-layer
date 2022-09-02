import os

from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from flask_s3 import FlaskS3

import main.config
from main.models import init_database
from main.routes import Api, api

s3 = FlaskS3()
jwt = None
executor: Executor = None


def create_app(config_name):
    global jwt
    app = Flask(__name__, template_folder='templates', static_url_path='')
    app.config.from_object(config.config_by_name[config_name])
    app.app_context().push()
    api.init_app(app)
    init_database()
    CORS(app)
    return app



