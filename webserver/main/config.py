import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    OTP_TIMEOUT_IN_MINUTES = 60
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    COOKIE_EXPIRY = 60000
    PORT = 9900
    FLASKS3_BUCKET_NAME = os.getenv('static_bucket_name')
    FLASKS3_FILEPATH_HEADERS = {r'.css$': {'Content-Type': 'text/css; charset=utf-8'},
                                r'.js$': {'Content-Type': 'text/javascript'}}
    FLASKS3_ACTIVE = os.getenv("flask_s3_active", "True") == "True"
    FLASKS3_GZIP = True
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    JWT_TOKEN_LOCATION = ['headers']
    S3_PRIVATE_BUCKET = os.getenv("PRIVATE_BUCKET")
    # below is valid for tokens coming in as part of query_params
    JWT_QUERY_STRING_NAME = "token"
    # Set the secret key to sign the JWTs with
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DOMAIN = "nic2004:52110"
    CITY_CODE = "std:080"
    COUNTRY_CODE = "IND"
    BAP_TTL = "20"
    BECKN_SECURITY_ENABLED = False
    BAP_PRIVATE_KEY = os.getenv("BAP_PRIVATE_KEY", "some-key")
    BAP_PUBLIC_KEY = os.getenv("BAP_PUBLIC_KEY", "some-key")
    BAP_ID = os.getenv("BAP_ID", "buyer-app.ondc.org")
    BAP_UNIQUE_KEY_ID = os.getenv("BAP_UNIQUE_KEY_ID", "207")
    REGISTRY_BASE_URL = "https://staging.registry.ondc.org"
    TTL_IN_SECONDS = int(os.getenv("TTL_IN_SECONDS", "3600"))
    VERIFICATION_ENABLE = os.getenv("VERIFICATION_ENABLE", "True") == "True"
    RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "bpp_protocol")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    QUEUE_ENABLE = os.getenv("QUEUE_ENABLE", "False") == "True"


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    ENV = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5433/flask"
    BAP_URL = "http://localhost:9002/protocol/v1"
    MONGO_DATABASE_HOST = "localhost"
    MONGO_DATABASE_PORT = 27017
    MONGO_DATABASE_NAME = "sandbox_bap"
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT", "https://616e-2409-4042-4d8d-a7b7-c127-cb03-c9c2-ecae.in.ngrok.io/clientApis/response")


class TestingConfig(Config):
    DEBUG = True
    PORT = 9901
    SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5433/flask"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOMAIN = "http://localhost:9900"
    PROPOGATE_EXCEPTIONS = True
    REDSHIFT_ANALYTICS_SCHEMA = "analytics"


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    JWT_COOKIE_CSRF_PROTECT = False
    MMI_CLIENT_ID = os.getenv("MMI_CLIENT_ID")
    MMI_CLIENT_SECRET = os.getenv("MMI_CLIENT_SECRET")
    MMI_ADVANCE_API_KEY = os.getenv("MMI_ADVANCE_API_KEY")
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9002/protocol/v1")
    MONGO_DATABASE_HOST = os.getenv("MONGO_DATABASE_HOST", "mongo")
    MONGO_DATABASE_PORT = int(os.getenv("MONGO_DATABASE_PORT", 27017))
    MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "sandbox_bap")
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT", "http://localhost:3001/clientApis/response")


class PreProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    JWT_COOKIE_CSRF_PROTECT = False
    MMI_CLIENT_ID = os.getenv("MMI_CLIENT_ID")
    MMI_CLIENT_SECRET = os.getenv("MMI_CLIENT_SECRET")
    MMI_ADVANCE_API_KEY = os.getenv("MMI_ADVANCE_API_KEY")
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9002/protocol/v1")
    MONGO_DATABASE_HOST = os.getenv("MONGO_DATABASE_HOST", "mongo")
    MONGO_DATABASE_PORT = int(os.getenv("MONGO_DATABASE_PORT", 27017))
    MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "sandbox_bap")
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT", "http://localhost:3001/clientApis/response")
    REGISTRY_BASE_URL = "https://preprod.registry.ondc.org/ondc"
    BAP_PRIVATE_KEY = os.getenv("BAP_PRIVATE_KEY", "some_key")
    BAP_PUBLIC_KEY = os.getenv("BAP_PUBLIC_KEY", "some_key")
    BAP_ID = os.getenv("BAP_ID", "buyer-app-preprod.ondc.org")
    BAP_UNIQUE_KEY_ID = os.getenv("BAP_UNIQUE_KEY_ID", "96c81878-f327-457e-8835-5b35bb20f099")


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
    pre_prod=PreProductionConfig,
)

key = Config.SECRET_KEY


def get_config_by_name(config_name, default=None, env_param_name=None):
    config_env = os.getenv(env_param_name or "ENV")
    config_value = default
    if config_env:
        config_value = getattr(config_by_name[config_env](), config_name, default)
    return config_value


def get_email_config_value_for_name(config_name):
    email_config_value = get_config_by_name("SES") or {}
    config = email_config_value.get(config_name)
    return config


if __name__ == '__main__':
    os.environ["ENV"] = "light"
    print(get_config_by_name("DOMAIN"))

    os.environ["ENV"] = "prod"
    print(get_email_config_value_for_name("from_email"))
