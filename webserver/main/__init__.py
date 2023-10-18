

import main.config


def create_app(config_name):
    from flask import Flask
    from flask_cors import CORS

    from main.models import init_database
    from main.routes import Api, api

    app = Flask(__name__, template_folder='templates', static_url_path='')
    app.config.from_object(config.config_by_name[config_name])
    app.app_context().push()
    api.init_app(app)
    init_database()
    CORS(app)
    return app



