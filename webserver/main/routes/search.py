from flask import g, request
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main import constant
from main.service.search import add_search_catalogues, get_catalogues_for_message_id, gateway_search
from main.utils.decorators import validate_auth_header
from main.utils.original_schema_utils import validate_data_with_original_schema
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

search_namespace = Namespace('search', description='Search Namespace')


@search_namespace.route("/search")
class GatewaySearch(Resource):
    def post(self):
        search_request = request.get_json()
        return gateway_search(search_request)


@search_namespace.route("/v1/on_search")
class AddSearchCatalogues(Resource):
    path_schema = get_json_schema_for_given_path('/on_search')

    # @validate_auth_header
    @expects_json(path_schema)
    def post(self):
        resp = add_search_catalogues(g.data)
        response_schema = get_json_schema_for_response('/on_search')
        validate(resp, response_schema)
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

