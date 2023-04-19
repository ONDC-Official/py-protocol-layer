from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

issue_status_namespace = Namespace('issue_status', description='Issue Status Namespace')


@issue_status_namespace.route("/issue_status")
class BPPSelect(Resource):

    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('issue_status', request_payload)


@issue_status_namespace.route("/v1/on_issue_status")
class AddSelectResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_issue_status')

    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='on_issue_status')
        response_schema = get_json_schema_for_response('/on_issue_status')
        validate(resp, response_schema)
        return resp


@issue_status_namespace.route("/response/v1/on_issue_status")
class GetSelectResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_issue_status', **args)

