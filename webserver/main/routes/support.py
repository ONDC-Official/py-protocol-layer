from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate
from main.utils.logger import get_logger

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call
from main.service.utils import validate_auth_header
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

support_namespace = Namespace('support', description='Support Namespace')

logger = get_logger()

@support_namespace.route("/support")
class BPPSupport(Resource):
    path_schema = get_json_schema_for_given_path('/support')

    @expects_json(path_schema)
    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('support', request_payload)


@support_namespace.route("/v1/on_support")
class AddSupportResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_support')

    @validate_auth_header
    @expects_json(path_schema)
    def post(self):
        logger.info(g.data)
        resp = add_bpp_response(g.data, request_type='on_support')
        response_schema = get_json_schema_for_response('/on_support')
        validate(resp, response_schema)
        return resp


@support_namespace.route("/response/v1/on_support")
class GetSupportResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_support', **args)

