from flask import g
from funcy import merge

from main import jwt
from main.config import get_config_by_name
from main.service.utils import password_hash
from main.logger.custom_logging import log


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    # need to consider the scenario where user might not be present
    return {}