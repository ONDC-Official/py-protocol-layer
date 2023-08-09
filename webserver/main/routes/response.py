from flask import request
from flask_restx import Namespace, Resource, reqparse

from main import constant
from main.service.common import get_bpp_response_for_message_id
from main.service.search import get_item_catalogues, get_item_details, get_item_attributes, get_item_attribute_values

response_namespace = Namespace('response', description='Response Namespace')


@response_namespace.route("/items")
class GetCataloguesForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("priceMin", dest="price_min", type=float, required=False)
        parser.add_argument("priceMax", dest="price_max", type=float, required=False)
        parser.add_argument("rating", dest="rating", type=float, required=False)
        parser.add_argument("name", dest="name", type=str, required=False)
        parser.add_argument("providerIds", dest="provider_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("categoryIds", dest="category_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("fulfillmentIds", dest="fulfillment_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("sortField", dest="sort_field", required=False, choices=[constant.PRICE, constant.RATING])
        parser.add_argument("sortOrder", dest="sort_order", required=False, choices=['asc', 'desc'])
        parser.add_argument("pageNumber", dest="page_number", type=int, default=1)
        parser.add_argument("limit", dest="limit", required=False, type=int, default=10)
        return parser.parse_args()

    def get(self):
        all_args = request.args
        product_attrs = {}
        for k, v in all_args.items():
            if "product_attr_" in k:
                attr_name = k.split("product_attr_")[1]
                product_attrs[attr_name] = v.split(",")
        args = self.create_parser_with_args()
        args['product_attrs'] = product_attrs
        return get_item_catalogues(**args)


@response_namespace.route("/items/<string:item_id>")
class GetCataloguesForMessageId(Resource):

    def get(self, item_id):
        return get_item_details(item_id)


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


@response_namespace.route("/attributes")
class GetItemAttributes(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("category", required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_item_attributes(args["category"])


@response_namespace.route("/attribute-values")
class GetItemAttributeValues(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("attribute_code", required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_item_attribute_values(args["attribute_code"])
