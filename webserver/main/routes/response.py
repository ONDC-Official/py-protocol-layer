from flask_restx import Namespace, Resource, reqparse

from main import constant
from main.service.common import get_bpp_response_for_message_id
from main.service.search import get_catalogues_for_message_id

response_namespace = Namespace('response', description='Response Namespace')


@response_namespace.route("/items")
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


@response_namespace.route("/response")
class GetResponseForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        parser.add_argument("requestType", dest='request_type', required=True)
        parser.add_argument("version", dest='version', default="1.2.0")
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(**args)
