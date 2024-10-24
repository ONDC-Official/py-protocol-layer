import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
all_domains_str = "ONDC:RET10,ONDC:RET11,ONDC:RET12,ONDC:RET13,ONDC:RET14,ONDC:RET15,ONDC:RET16,ONDC:RET17,ONDC:RET18" \
                  ",ONDC:RET19,ONDC:RET20,ONDC:AGR10"
all_cities_str = "std:06274,std:0451,std:0120,std:0512,std:05842,std:0522,std:06243,std:04286,std:05547,std:0474," \
                 "std:0121,std:04266,std:04142,std:0551,std:0124,std:0591,std:0364,std:04254,std:079,std:0129," \
                 "std:06152,std:08922,std:04362,std:05263,std:0261,std:0487,std:08252,std:01342,std:0832217," \
                 "std:0581,std:07486,std:0132,std:0484,std:0416,std:05248,std:0191,std:04546,std:0260,std:0427," \
                 "std:08262,std:0194,std:0435,std:08258,std:01334,std:04652,std:04147,std:0421,std:08572,std:044," \
                 "std:0731,std:02836,std:0641,std:06224,std:0462,std:02762,std:06244,std:04364,std:04259,std:03592," \
                 "std:022,std:06255,std:0571,std:0281,std:07162,std:0532,std:08232,std:02792,std:06276,std:02838," \
                 "std:04146,std:08373,std:0154,std:04175,std:04324,std:04632,std:0477,std:02766,std:05921,std:06345," \
                 "std:02632,std:06324,std:0471,std:04174,std:05362,std:0479,std:0824,std:0131,std:0621,std:0265," \
                 "std:020,std:04567,std:080,std:01382,std:06272,std:040,std:0497,std:0452,std:033,std:0755,std:0821," \
                 "std:05872,std:05692,std:0422,std:04116,std:05852,std:04563,std:0612,std:0172,std:06452,std:0268," \
                 "std:04575,std:0820,std:04112,std:02692,std:0135,std:01461,std:0832,std:06466,std:02752,std:0431," \
                 "std:0424,std:04344,std:08676,std:0278,std:0542,std:0562,std:0671,std:05862,std:0288,std:02637," \
                 "std:0141,std:01421,std:011,std:05271,std:05542,std:05282,std:08288,std:06755"


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
    REGISTRY_BASE_URL = os.getenv("REGISTRY_BASE_URL", "https://preprod.registry.ondc.org/ondc")
    TTL_IN_SECONDS = int(os.getenv("TTL_IN_SECONDS", "18000"))
    VERIFICATION_ENABLE = os.getenv("VERIFICATION_ENABLE", "True") == "True"
    RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "bpp_protocol")
    ELASTIC_SEARCH_QUEUE_NAME = os.getenv("ELASTIC_SEARCH_QUEUE_NAME", "catalog_indexing")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_CREDS = os.getenv("RABBITMQ_CREDS", "False") == "True"
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "username")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
    QUEUE_ENABLE = os.getenv("QUEUE_ENABLE", "False") == "True"
    ELASTIC_SEARCH_QUEUE_ENABLE = os.getenv("ELASTIC_SEARCH_QUEUE_ENABLE", "False") == "True"
    DUMP_ALL_REQUESTS = os.getenv("DUMP_ALL_REQUESTS", "False") == "True"
    API_TOKEN = os.getenv("API_TOKEN", "testing_random_123")
    MAX_CONSUME_MESSAGE_TIME = int(os.getenv("MAX_CONSUME_MESSAGE_TIME", "30"))
    CONSUMER_MAX_WORKERS = int(os.getenv("CONSUMER_MAX_WORKERS", "10"))
    PARALLEL_PROCESSES = int(os.getenv("PARALLEL_PROCESSES", "10"))
    MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL", "mongodb://localhost:27017")
    # MONGO_DATABASE_URL = "mongodb://mongo1:27017,mongo2:27018/?replicaSet=my-replica-set&readPreference=secondary"
    IS_TEST = os.getenv("IS_TEST", "False") == "True"
    DOMAIN_LIST = [d.strip() for d in os.getenv("DOMAIN_LIST", all_domains_str).split(",")]
    CITY_LIST = [c.strip() for c in os.getenv("CITY_LIST", all_cities_str).split(",")]
    NO_DASHBOARD_ENDPOINT = os.getenv("NO_DASHBOARD_ENDPOINT", "https://analytics-api-pre-prod.aws.ondc.org")
    NO_DASHBOARD_BEARER_TOKEN = os.getenv("NO_DASHBOARD_BEARER_TOKEN", "token")
    BAP_FINDER_FEE_TYPE = os.getenv("BAP_FINDER_FEE_TYPE", "percent")
    BAP_FINDER_FEE_AMOUNT = os.getenv("BAP_FINDER_FEE_AMOUNT", "3")


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    ENV = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5433/flask"
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9900/protocol/v1")
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
    os.environ["ENV"] = "dev"
    print(get_config_by_name("DOMAIN_LIST"))
    print(get_config_by_name("CITY_LIST"))

    # os.environ["ENV"] = "prod"
    # print(get_email_config_value_for_name("from_email"))
