from flask import g
from flask_expects_json import expects_json
from flask_restx import Namespace, Resource, reqparse
from jsonschema import validate

from main.service.search import add_search_catalogues, get_catalogues_for_message_id
from main.utils.schema_utils import get_json_schema_for_given_path, get_json_schema_for_response

search_namespace = Namespace('search', description='Search Namespace')


@search_namespace.route("/v1/on_search")
class AddSearchCatalogues(Resource):
    path_schema = get_json_schema_for_given_path('/on_search')

    @expects_json(path_schema)
    def post(self):
        resp = add_search_catalogues(g.data)
        response_schema = get_json_schema_for_response('/on_search')
        validate(resp, response_schema)
        return resp
        # data = request.get_json()
        # if data['context'].get('core_version') and type(data['message'].get('catalog')) == dict:
        #     return add_search_catalogues(data)
        # else:
        #     return {"error": "core_version absent"}, 400


@search_namespace.route("/response/v1/on_search")
class GetCataloguesForMessageId(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("messageId", dest='message_id', required=True)
        return parser.parse_args()

    def get(self):
        args = self.create_parser_with_args()
        return get_catalogues_for_message_id(**args)

