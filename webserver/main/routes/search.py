from flask import g, request
from flask_restx import Namespace, Resource, reqparse

from main import constant
from main.service.search import get_catalogues_for_message_id, gateway_search
from main.utils.validation import validate_payload_schema_based_on_version

search_namespace = Namespace('search', description='Search Namespace')


@search_namespace.route("/search")
class GatewaySearch(Resource):

    def post(self):
        request_payload = request.get_json()
        # validate schema based on context version
        resp = validate_payload_schema_based_on_version(request_payload, 'search')
        if resp is None:
            return gateway_search(request_payload)
        else:
            return resp


@search_namespace.route("/response/v1/on_search")
class GetCataloguesForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        parser.add_argument("priceMin", dest="price_min", type=float, required=False)
        parser.add_argument("priceMax", dest="price_max", type=float, required=False)
        parser.add_argument("rating", dest="rating", type=float, required=False)
        parser.add_argument("providerIds", dest="provider_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("categoryIds", dest="category_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("fulfillmentIds", dest="fulfillment_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("sortField", dest="sort_field", required=False, choices=[constant.PRICE, constant.RATING])
        parser.add_argument("sortOrder", dest="sort_order", required=False, choices=['asc', 'desc'])
        parser.add_argument("pageNumber", dest="page_number", type=int, default=1)
        parser.add_argument("limit", dest="limit", required=False, type=int, default=10)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_catalogues_for_message_id(**args)

