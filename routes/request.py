from flask import request
from flask_restx import Namespace, Resource

from authentication import authenticate
from services import request_dump_and_forward
from validations import validate_payload

request_namespace = Namespace('request', description='Request Namespace')


@request_namespace.route("/search")
class Search(Resource):

    @authenticate
    @validate_payload("search")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/select")
class Select(Resource):

    @authenticate
    @validate_payload("select")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/init")
class Init(Resource):

    @authenticate
    @validate_payload("init")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/confirm")
class Confirm(Resource):

    @authenticate
    @validate_payload("confirm")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/update")
class Update(Resource):

    @authenticate
    @validate_payload("update")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/cancel")
class Cancel(Resource):

    @authenticate
    @validate_payload("cancel")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/status")
class Status(Resource):

    @authenticate
    @validate_payload("status")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/track")
class Track(Resource):

    @authenticate
    @validate_payload("track")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/support")
class Support(Resource):

    @authenticate
    @validate_payload("support")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/rating")
class Rating(Resource):

    @authenticate
    @validate_payload("rating")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/issue")
class Issue(Resource):

    @authenticate
    @validate_payload("issue")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)


@request_namespace.route("/issue_status")
class IssueStatus(Resource):

    @authenticate
    @validate_payload("issue_status")
    def post(self, nack_resp):
        return request_dump_and_forward(request.get_json(), dict(request.headers), nack_resp)
