from flask_restx import Namespace, Resource, reqparse

from services.request_dump import get_request_payloads, get_request_logs

request_dump_namespace = Namespace('request_dump', description='Request Namespace')


@request_dump_namespace.route("/request-dump")
class RequestDump(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("action", dest='action', required=True)
        parser.add_argument("messageId", dest="message_id", required=True)
        parser.add_argument("statusCode", dest="status_code", required=False, type=int)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_request_payloads(**args)


@request_dump_namespace.route("/request-logs")
class GetRequestLogs(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("action", required=False)
        parser.add_argument("transaction_id", required=False)
        parser.add_argument("message_id", required=False)
        parser.add_argument("bpp_id", required=False)
        parser.add_argument("sort_order", required=False, choices=['asc', 'desc'])
        parser.add_argument("page_number", type=int, default=1)
        parser.add_argument("limit", dest="limit", required=False, type=int, default=10)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_request_logs(**args)



