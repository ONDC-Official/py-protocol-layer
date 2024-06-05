from flask import request
from flask_restx import Namespace, Resource

from authentication import authenticate
from services import request_dump_and_forward
from validations import validate_payload

request_namespace = Namespace('request', description='Request Namespace')


@request_namespace.route("/v1/search")
class Search(Resource):

    @authenticate
    @validate_payload("search")
    def post(self):
        request_dump_and_forward(request.get_json(), request.headers)