from flask import request
from flask_restx import Namespace, Resource

from authentication import authenticate
from services import request_dump_and_forward
from validations import validate_payload

callback_namespace = Namespace('callback', description='Callback Namespace')


@callback_namespace.route("/on_search")
class Search(Resource):

    @authenticate
    @validate_payload("on_search")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_select")
class Select(Resource):

    @authenticate
    @validate_payload("on_select")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_init")
class Init(Resource):

    @authenticate
    @validate_payload("on_init")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_confirm")
class Confirm(Resource):

    @authenticate
    @validate_payload("on_confirm")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_update")
class Update(Resource):

    @authenticate
    @validate_payload("on_update")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_cancel")
class Cancel(Resource):

    @authenticate
    @validate_payload("on_cancel")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_status")
class Status(Resource):

    @authenticate
    @validate_payload("on_status")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_track")
class Track(Resource):

    @authenticate
    @validate_payload("on_track")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_support")
class Support(Resource):

    @authenticate
    @validate_payload("on_support")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_rating")
class Rating(Resource):

    @authenticate
    @validate_payload("on_rating")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_issue")
class Issue(Resource):

    @authenticate
    @validate_payload("on_issue")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))


@callback_namespace.route("/on_issue_status")
class IssueStatus(Resource):

    @authenticate
    @validate_payload("on_issue_status")
    def post(self):
        return request_dump_and_forward(request.get_json(), dict(request.headers))
