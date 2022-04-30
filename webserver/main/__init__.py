import os

from authlib.integrations.sqla_oauth2 import create_bearer_token_validator
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from flask_jwt_extended import JWTManager
from flask_s3 import FlaskS3

import main.config
from main.controller.oauth2_server_controller import AuthorizationCodeGrant, RefreshTokenGrant
from main.models import init_app
from main.models.oauth2_models import get_oauth_authorization, get_oauth_resource_protector
from main.models.redshift_db import initialize_redshift_session
from main.routes import Api, api, trip_metadata_api
from main.utils.model_serializer import CustomJSONEncoder

s3 = FlaskS3()
jwt = None
executor: Executor = None


def create_app(config_name):
    global jwt
    app = Flask(__name__, template_folder='templates', static_url_path='')
    app.config.from_object(config.config_by_name[config_name])
    app.app_context().push()

    if config_name in ["trip_metadata_dev", "trip_metadata_prod"]:
        trip_metadata_api.init_app(app)
        init_app(app, is_init_db=True, is_init_kafka=True)
        jwt = JWTManager(app)
    else:
        api.init_app(app)
        update_app_dashboard(app)
        init_app(
            app=app,
            is_init_db=True,
            is_init_kafka=False,
            is_re_init_db=os.getenv("RECREATE_TABLE", "False") == "True",
            is_create_admin_logins=os.getenv("CREATE_ADMIN", "False") == "True",
        )
        initialize_redshift_session(app, bind="redshift_analytics", schema="REDSHIFT_ANALYTICS_SCHEMA")
    return app


def update_app_dashboard(app):
    global jwt, executor
    s3.init_app(app)
    executor = Executor(app)
    CORS(app)
    jwt = JWTManager(app)
    # app.json_encoder = CustomJSONEncoder
    jwt._set_error_handler_callbacks(api)
    config_oauth(app)
    return app


def config_oauth(app):
    get_oauth_authorization().init_app(app)

    # support all grants
    get_oauth_authorization().register_grant(grants.ClientCredentialsGrant)
    get_oauth_authorization().register_grant(AuthorizationCodeGrant, [CodeChallenge()])
    get_oauth_authorization().register_grant(RefreshTokenGrant)

    # support revocation
    # revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    # get_oauth_authorization().register_endpoint(revocation_cls)

    # protect resource


