from flask import g
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.common import add_bpp_response, get_bpp_response_for_message_id
from main.service.utils import validate_auth_header
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

cancellation_reasons_namespace = Namespace('cancellation_reasons', description='Cancellation Reasons Namespace')


@cancellation_reasons_namespace.route("/v1/cancellation_reasons")
class AddCancellationReasonsResponse(Resource):
    path_schema = get_json_schema_for_given_path('/cancellation_reasons')

    @validate_auth_header
    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='cancellation_reasons')
        response_schema = get_json_schema_for_response('/cancellation_reasons')
        validate(resp, response_schema)
        return resp


@cancellation_reasons_namespace.route("/response/v1/on_cancellation_reasons")
class GetCancellationReasonsResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_cancellation_reasons', **args)

