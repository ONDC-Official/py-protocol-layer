import os

from flask import Flask
from flask_cors import CORS

import config
from models import init_database
from routes import api


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config_by_name[config_name])
    app.app_context().push()
    api.init_app(app)
    init_database()
    CORS(app)
    return app


if __name__ == '__main__':
    created_app = create_app(os.getenv("ENV", "dev"))
    created_app.run(host="0.0.0.0", port=created_app.config["PORT"])
