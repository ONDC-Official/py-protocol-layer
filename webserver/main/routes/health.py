from flask import request
from flask_restx import Namespace, Resource

from main import constant
from main.business_rule_validation import validate_business_rules
from main.config import get_config_by_name
from main.logger.custom_logging import log
from main.models.catalog import SearchType
from main.repository.ack_response import get_ack_response
from main.service import send_message_to_queue_for_given_request, send_message_to_elastic_search_queue
from main.service.common import add_bpp_response, dump_request_payload, update_dumped_request_with_response
from main.service.search import add_search_catalogues, dump_on_search_payload, add_incremental_search_catalogues
from main.service.utils import validate_auth_header, dump_validation_failure_request
from main.utils.decorators import MeasureTime
from main.utils.json_utils import clean_nones
from main.utils.validation import validate_payload_schema_based_on_version

health_namespace = Namespace('health', description='Health Namespace')


@health_namespace.route("/")
class Health(Resource):

    def get(self):
        return "Healthy", 200
