from flask import request
from flask_restx import Namespace, Resource

from authentication import authenticate
from services import request_dump_and_forward
from validations import validate_payload

callback_namespace = Namespace('callback', description='Callback Namespace')


@callback_namespace.route("/v1/on_search")
class Search(Resource):

    @authenticate
    @validate_payload("on_search")
    def post(self):
        request_dump_and_forward(request.get_json(), request.headers)