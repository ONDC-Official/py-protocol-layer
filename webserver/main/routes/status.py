from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

status_namespace = Namespace('status', description='Status Namespace')


@status_namespace.route("/status")
class BPPStatus(Resource):

    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('status', request_payload)


@status_namespace.route("/v1/on_status")
class AddStatusResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_status')

    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='on_status')
        response_schema = get_json_schema_for_response('/on_status')
        validate(resp, response_schema)
        return resp


@status_namespace.route("/response/v1/on_status")
class GetStatusResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_status', **args)

