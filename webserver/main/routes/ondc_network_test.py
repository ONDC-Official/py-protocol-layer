from flask import request
from flask_restx import Namespace, Resource

from main import constant
from main.repository.ack_response import get_ack_response
from main.service.search import add_search_catalogues_for_test
from main.utils.decorators import MeasureTime
from main.utils.validation import validate_payload_schema_based_on_version

ondc_network_test_namespace = Namespace('ondc_network', description='ONDC Network Namespace')


@ondc_network_test_namespace.route("/v1/on_search")
class GatewayOnSearch(Resource):

    @MeasureTime
    def post(self):
        request_payload = request.get_json()
        # validate schema based on context version
        resp = validate_payload_schema_based_on_version(request_payload, 'on_search')
        if resp is None:
            return add_search_catalogues_for_test(request_payload)
        return resp


@ondc_network_test_namespace.route("/v1/on_select")
class AddSelectResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_select')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_init")
class AddInitResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_init')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_confirm")
class AddConfirmResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_confirm')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_cancel")
class AddCancelResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_cancel')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/cancellation_reasons")
class AddCancellationReasonsResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_cancellation_reasons')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_issue")
class AddIssueResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_issue')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_issue_status")
class AddIssueStatusResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_issue_status')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_rating")
class AddRatingResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_rating')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_status")
class AddStatusResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_status')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_support")
class AddSupportResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_support')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_track")
class AddTrackResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_track')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp


@ondc_network_test_namespace.route("/v1/on_update")
class AddUpdateResponse(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'on_update')
        if resp is None:
            return get_ack_response(context=request_payload[constant.CONTEXT], ack=True)
        return resp
