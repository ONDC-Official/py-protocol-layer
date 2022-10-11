from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

update_namespace = Namespace('update', description='Update Namespace')


@update_namespace.route("/update")
class BPPUpdate(Resource):

    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('update', request_payload)


@update_namespace.route("/v1/on_update")
class AddUpdateResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_update')

    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='on_update')
        response_schema = get_json_schema_for_response('/on_update')
        validate(resp, response_schema)
        return resp


@update_namespace.route("/response/v1/on_update")
class GetUpdateResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_update', **args)

