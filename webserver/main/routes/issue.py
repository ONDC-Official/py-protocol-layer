from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

issue_namespace = Namespace('issue', description='Issue Namespace')


@issue_namespace.route("/issue")
class BPPIssue(Resource):

    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('issue', request_payload)


@issue_namespace.route("/v1/on_issue")
class AddIssueResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_issue')

    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='on_issue')
        response_schema = get_json_schema_for_response('/on_issue')
        validate(resp, response_schema)
        return resp


@issue_namespace.route("/response/v1/on_issue")
class GetSelectResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_issue', **args)
