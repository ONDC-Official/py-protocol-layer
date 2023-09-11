import json
import os

from flask import request
from flask_restx import Api as BaseAPI
from jsonschema import ValidationError
from werkzeug.exceptions import BadRequest

from main import constant
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response
from main.routes.cron import cron_namespace
from main.routes.ondc_network import ondc_network_namespace
from main.routes.client import client_namespace
from main.routes.response import response_namespace
from main.utils.schema_utils import transform_json_schema_error


class Api(BaseAPI):
    def _register_doc(self, app_or_blueprint):
        # HINT: This is just a copy of the original implementation with the last line commented out.
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        # app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)

    @property
    def base_path(self):
        return ''


api = Api(
    title='ONDC API',
    version='1.0',
    description='Rest api for ONDC dashboard project',
    doc='/swagger/' if os.getenv("ENV") != None else False
)

# api.render_root()


@api.errorhandler(BadRequest)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        # validate_data_with_original_schema(request.get_json(), '/on_select', passing_in_python_protocol=False)
        # log(f"data: {request.get_json()} \n error: {error.description}")
        context = json.loads(request.data)[constant.CONTEXT]
        error_message = transform_json_schema_error(error.description)
        return get_ack_response(context=context, ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error_message}), 400
    # handle other "Bad Request"-errors
    return str(error), 500


@api.errorhandler(ValidationError)
def bad_request(error):
    return {'error': str(error), 'message': error.message}, 400


api.add_namespace(ondc_network_namespace, path='/protocol')
api.add_namespace(client_namespace, path='/protocol')
api.add_namespace(response_namespace, path='/protocol')
api.add_namespace(cron_namespace, path='/protocol')
