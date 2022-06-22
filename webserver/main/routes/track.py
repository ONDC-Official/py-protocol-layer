from flask import g
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main import constant
from main.service.common import add_bpp_response, get_bpp_response_for_message_id
from main.utils.original_schema_utils import validate_data_with_original_schema
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

track_namespace = Namespace('track', description='Track Namespace')


@track_namespace.route("/v1/on_track")
class AddTrackResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_track')

    @expects_json(path_schema)
    def post(self):
        resp = add_bpp_response(g.data, request_type='on_track')
        response_schema = get_json_schema_for_response('/on_track')
        validate(resp, response_schema)
        return resp


@track_namespace.route("/response/v1/on_track")
class GetTrackResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(request_type='on_track', **args)

