from flask_restx import Namespace, Resource, reqparse

from main.service.on_search_logs import get_on_search_payloads

logs_namespace = Namespace('logs', description='Response Namespace')


@logs_namespace.route("/on-search-logs")
class GetCataloguesForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("transaction_id", required=False)
        parser.add_argument("message_id", required=False)
        parser.add_argument("bpp_id", required=False)
        parser.add_argument("domain", required=False)
        parser.add_argument("city", required=False)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_on_search_payloads(**args)
