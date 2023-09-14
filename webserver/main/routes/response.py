from flask import request
from flask_restx import Namespace, Resource, reqparse

from main import constant
from main.service.common import get_bpp_response_for_message_id
from main.service.search import get_item_catalogues, get_item_details, get_item_attributes, get_item_attribute_values, \
    get_custom_menus, get_providers, get_locations, get_custom_menu_details, get_provider_details, get_location_details

response_namespace = Namespace('response', description='Response Namespace')


@response_namespace.route("/items")
class GetCataloguesForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("priceMin", dest="price_min", type=float, required=False)
        parser.add_argument("priceMax", dest="price_max", type=float, required=False)
        parser.add_argument("rating", dest="rating", type=float, required=False)
        parser.add_argument("name", dest="name", type=str, required=False)
        parser.add_argument("customMenu", dest="custom_menu", type=str, required=False)
        parser.add_argument("providerIds", dest="provider_ids", type=lambda x: x.split(","), required=False)
        parser.add_argument("locationIds", dest="location_ids", type=lambda x: x.split(","), required=False)
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
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_bpp_response_for_message_id(**args)


@response_namespace.route("/custom-menus")
class GetCustomMenus(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("domain", required=False)
        parser.add_argument("provider", required=False)
        parser.add_argument("category", required=False)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_custom_menus(**args)


@response_namespace.route("/attributes")
class GetItemAttributes(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("domain", required=False)
        parser.add_argument("category", required=False)
        parser.add_argument("provider", required=False)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_item_attributes(**args)


@response_namespace.route("/attribute-values")
class GetItemAttributeValues(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("attribute_code", required=True)
        parser.add_argument("category", required=False)
        parser.add_argument("provider", required=False)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_item_attribute_values(**args)


@response_namespace.route("/providers")
class GetItemProviders(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("domain", required=False)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_providers(**args)


@response_namespace.route("/locations")
class GetItemLocations(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("domain", required=False)
        parser.add_argument("provider", required=False)
        parser.add_argument("latitude", required=False, type=float)
        parser.add_argument("longitude", required=False, type=float)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_locations(**args)


@response_namespace.route("/custom-menus/<string:custom_menu_id>")
class GetCustomMenu(Resource):

    def get(self, custom_menu_id):
        return get_custom_menu_details(custom_menu_id)


@response_namespace.route("/providers/<string:provider_id>")
class GetProvider(Resource):

    def get(self, provider_id):
        return get_provider_details(provider_id)


@response_namespace.route("/locations/<string:location_id>")
class GetLocation(Resource):

    def get(self, location_id):
        return get_location_details(location_id)
