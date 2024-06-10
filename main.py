import os

from flask import Flask
from flask_cors import CORS

import config
from models import init_database
from routes import api


def create_app(config_name):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config.config_by_name[config_name])
    flask_app.app_context().push()
    api.init_app(flask_app)
    init_database()
    CORS(flask_app)
    return flask_app


app = create_app(os.getenv("ENV", "dev"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config["PORT"])
