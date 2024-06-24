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
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    COOKIE_EXPIRY = 60000
    PORT = os.getenv("PORT", "9900")
    JWT_TOKEN_LOCATION = ['headers']
    # below is valid for tokens coming in as part of query_params
    JWT_QUERY_STRING_NAME = "token"
    # Set the secret key to sign the JWTs with
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    CITY_CODE = "std:080"
    COUNTRY_CODE = "IND"
    APP_TTL = "20"
    TYPE = os.getenv("TYPE", "RETAIL_BAP")
    APP_PRIVATE_KEY = os.getenv("APP_PRIVATE_KEY", "some-key")
    APP_PUBLIC_KEY = os.getenv("APP_PUBLIC_KEY", "some-key")
    APP_ID = os.getenv("APP_ID", "buyer-app.ondc.org")
    APP_UNIQUE_KEY_ID = os.getenv("APP_UNIQUE_KEY_ID", "207")
    REGISTRY_BASE_URL = os.getenv("REGISTRY_BASE_URL", "https://preprod.registry.ondc.org/ondc")
    TTL_IN_SECONDS = int(os.getenv("TTL_IN_SECONDS", "18000"))
    VERIFICATION_ENABLE = os.getenv("VERIFICATION_ENABLE", "True") == "True"
    RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "bpp_protocol")
    ELASTIC_SEARCH_QUEUE_NAME = os.getenv("ELASTIC_SEARCH_QUEUE_NAME", "catalog_indexing")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    QUEUE_ENABLE = os.getenv("QUEUE_ENABLE", "False") == "True"
    ELASTIC_SEARCH_QUEUE_ENABLE = os.getenv("ELASTIC_SEARCH_QUEUE_ENABLE", "False") == "True"
    API_TOKEN = os.getenv("API_TOKEN", "testing_random_123")
    MAX_CONSUME_MESSAGE_TIME = int(os.getenv("MAX_CONSUME_MESSAGE_TIME", "30"))
    CONSUMER_MAX_WORKERS = int(os.getenv("CONSUMER_MAX_WORKERS", "100"))
    MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL", "mongodb://localhost:27017")
    MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "sandbox_bap")
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT", "client")
    IGM_WEBHOOK_ENDPOINT = os.getenv("IGM_WEBHOOK_ENDPOINT", "igm")
    # MONGO_DATABASE_URL = "mongodb://mongo1:27017,mongo2:27018/?replicaSet=my-replica-set&readPreference=secondary"
    IS_TEST = os.getenv("IS_TEST", "False") == "True"
    DOMAIN_LIST = [d.strip() for d in os.getenv("DOMAIN_LIST", all_domains_str).split(",")]
    CITY_LIST = [c.strip() for c in os.getenv("CITY_LIST", all_cities_str).split(",")]
    EXPECTED_RESPONSE_TIME = os.getenv("EXPECTED_RESPONSE_TIME", "PT1H")
    RQ_REDIS_URL = f"redis://{os.getenv('REDIS_URL', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1"
    RQ_ASYNC = os.getenv("RQ_ASYNC", "False") == "True"


class DevelopmentConfig(Config):
    """Development config."""
    DEBUG = True


class TestingConfig(Config):
    """Testing config."""
    TESTING = True


class ProductionConfig(Config):
    """Production config."""
    DEBUG = False
    TESTING = False


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)


def get_config_by_name(config_name, default=None, env_param_name=None):
    config_env = os.getenv(env_param_name or "ENV")
    config_value = default
    if config_env:
        config_value = getattr(config_by_name[config_env](), config_name, default)
    return config_value


if __name__ == '__main__':
    os.environ["ENV"] = "dev"

    # os.environ["ENV"] = "prod"
    # print(get_email_config_value_for_name("from_email"))
