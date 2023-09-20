from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate
from main.utils.logger import get_logger

from main.service.common import add_bpp_response, get_bpp_response_for_message_id, bpp_post_call,log_time_difference
from main.service.utils import validate_auth_header
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

track_namespace = Namespace('track', description='Track Namespace')

logger = get_logger()

@track_namespace.route("/track")
class BPPTrack(Resource):
    path_schema = get_json_schema_for_given_path('/track')

    @expects_json(path_schema)
    def post(self):
        request_payload = request.get_json()
        return bpp_post_call('track', request_payload)


@track_namespace.route("/v1/on_track")
class AddTrackResponse(Resource):
    path_schema = get_json_schema_for_given_path('/on_track')

    @validate_auth_header
    @expects_json(path_schema)
    def post(self):
        logger.info(g.data)
        resp = add_bpp_response(g.data, request_type='on_track')
        response_schema = get_json_schema_for_response('/on_track')
        validate(resp, response_schema)
        logger.info(resp)
        return resp


@track_namespace.route("/response/v1/on_track")
class GetTrackResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        track_request = get_bpp_response_for_message_id(request_type='track', **args)
        on_track_response = get_bpp_response_for_message_id(request_type='on_track', **args)

        log_time_difference(track_request,on_track_response)
        return on_track_response

