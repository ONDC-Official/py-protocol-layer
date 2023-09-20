from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate
from main.utils.logger import get_logger

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call, log_time_difference
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

issue_status_namespace = Namespace('issue_status', description='Issue Status Namespace')

logger = get_logger()

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
        logger.info(g.data)
        resp = add_bpp_response(g.data, request_type='on_issue_status')
        response_schema = get_json_schema_for_response('/on_issue_status')
        validate(resp, response_schema)
        logger.info(resp)
        return resp


@issue_status_namespace.route("/response/v1/on_issue_status")
class GetSelectResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        issue_status_request = get_bpp_response_for_message_id(request_type='issue_status', **args)
        on_issue_status_response = get_bpp_response_for_message_id(request_type='on_issue_status', **args)

        log_time_difference(issue_status_request,on_issue_status_response)
        return on_issue_status_response

