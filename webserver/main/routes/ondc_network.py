import json

from flask import request
from flask_restx import Namespace, Resource
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from main import constant
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response
from main.service.common import add_bpp_response
from main.service.search import add_search_catalogues
from main.service.utils import validate_auth_header
from main.utils.schema_utils import get_json_schema_for_given_path, transform_json_schema_error

ondc_network_namespace = Namespace('ondc_network', description='ONDC Network Namespace')


def validate_json_schema(request_payload, request_schema):
    try:
        validate(request_payload, request_schema)
        return None
    except ValidationError as e:
        error_message = transform_json_schema_error(e)
        context = json.loads(request.data)[constant.CONTEXT]
        return get_ack_response(context=context, ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error_message}), 400


@ondc_network_namespace.route("/v1/on_search")
class GatewayOnSearch(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_search')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_search_catalogues(request_payload)
        else:
            return resp


@ondc_network_namespace.route("/v1/on_select")
class AddSelectResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_select')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_select")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_init")
class AddInitResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_init')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_init")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_confirm")
class AddConfirmResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_confirm')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_confirm")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_cancel")
class AddCancelResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_cancel')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_cancel")
        else:
            return resp


@ondc_network_namespace.route("/v1/cancellation_reasons")
class AddCancellationReasonsResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/cancellation_reasons')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="cancellation_reasons")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_issue")
class AddIssueResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_issue')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_issue")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_issue_status")
class AddIssueStatusResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_issue_status')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_issue_status")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_rating")
class AddRatingResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_rating')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_rating")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_status")
class AddStatusResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_status')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_status")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_support")
class AddSupportResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_support')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_support")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_track")
class AddTrackResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_track')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_track")
        else:
            return resp


@ondc_network_namespace.route("/v1/on_update")
class AddUpdateResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        request_schema = get_json_schema_for_given_path('/on_update')
        resp = validate_json_schema(request_payload, request_schema)
        if resp is None:
            return add_bpp_response(request_payload, request_type="on_update")
        else:
            return resp
