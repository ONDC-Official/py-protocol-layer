from flask_restx import Namespace, Resource, reqparse

from services.request_dump import get_request_payloads

request_dump_namespace = Namespace('request_dump', description='Request Namespace')


@request_dump_namespace.route("/request-dump")
class RequestDump(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("action", dest='action', required=True)
        parser.add_argument("messageId", dest="message_id", required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_request_payloads(**args)
