from flask import request
from flask_restx import Namespace, Resource

from main import constant
from main.business_rule_validation import validate_business_rules
from main.config import get_config_by_name
from main.logger.custom_logging import log
from main.models.catalog import SearchType
from main.repository.ack_response import get_ack_response
from main.service import send_message_to_queue_for_given_request, send_message_to_elastic_search_queue
from main.service.common import add_bpp_response, dump_request_payload, update_dumped_request_with_response
from main.service.search import add_search_catalogues, dump_on_search_payload, add_incremental_search_catalogues
from main.service.utils import validate_auth_header, dump_validation_failure_request
from main.utils.decorators import MeasureTime
from main.utils.validation import validate_payload_schema_based_on_version

ondc_network_namespace = Namespace('ondc_network', description='ONDC Network Namespace')


@ondc_network_namespace.route("/v1/on_search")
class GatewayOnSearch(Resource):

    @MeasureTime
    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        # validate schema based on context version
        request_type = request.headers.get("X-ONDC-Search-Response", "full")
        if request_type == SearchType.FULL.value:
            resp = validate_payload_schema_based_on_version(request_payload, 'full_on_search')
            resp = validate_business_rules(request_payload, 'full_on_search') if resp is None else resp
        else:
            resp = validate_payload_schema_based_on_version(request_payload, 'incr_on_search')
            resp = validate_business_rules(request_payload, 'incr_on_search') if resp is None else resp

        if resp is None:
            if get_config_by_name('QUEUE_ENABLE') or get_config_by_name('ELASTIC_SEARCH_QUEUE_ENABLE'):
                doc_id = dump_on_search_payload(request_payload)
                message = {
                    "doc_id": str(doc_id),
                    "request_type": request_type,
                }
                send_message_to_queue_for_given_request(message) if get_config_by_name('QUEUE_ENABLE') else None
                send_message_to_elastic_search_queue(message) if get_config_by_name('ELASTIC_SEARCH_QUEUE_ENABLE') else None
                return get_ack_response(request_payload[constant.CONTEXT], ack=True)
            else:
                if request_type == SearchType.FULL.value:
                    return add_search_catalogues(request_payload)
                elif request_type == SearchType.INC.value:
                    return add_incremental_search_catalogues(request_payload)
        else:
            dump_validation_failure_request(request_payload, resp[0]["error"]["message"])
            return resp


@ondc_network_namespace.route("/v1/on_select")
class AddSelectResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_select request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_select')
        resp = validate_business_rules(request_payload, 'on_select') if resp is None else resp
        entry_object_id = dump_request_payload("on_select", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_select")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_select response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_init")
class AddInitResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_init request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_init')
        resp = validate_business_rules(request_payload, 'on_init') if resp is None else resp
        entry_object_id = dump_request_payload("on_init", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_init")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_init response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_confirm")
class AddConfirmResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_confirm request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_confirm')
        entry_object_id = dump_request_payload("on_confirm", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_confirm")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_confirm response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_cancel")
class AddCancelResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_cancel request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_cancel')
        entry_object_id = dump_request_payload("on_cancel", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_cancel")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_cancel response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/cancellation_reasons")
class AddCancellationReasonsResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the cancellation_reasons request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_cancellation_reasons')
        if resp is None:
            entry_object_id = dump_request_payload("on_cancellation_reasons", request_payload)
            resp = add_bpp_response(request_payload, request_type="on_cancellation_reasons")
            update_dumped_request_with_response(entry_object_id, resp)
            log(f"Got the cancellation_reasons response {resp}!")
            return resp
        else:
            log(f"Got the cancellation_reasons response {resp}!")
            return resp


@ondc_network_namespace.route("/v1/on_issue")
class AddIssueResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_issue request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_issue')
        entry_object_id = dump_request_payload("on_issue", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_issue")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_issue response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_issue_status")
class AddIssueStatusResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_issue_status request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_issue_status')
        entry_object_id = dump_request_payload("on_issue_status", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_issue_status")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_issue_status response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_rating")
class AddRatingResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_rating request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_rating')
        entry_object_id = dump_request_payload("on_rating", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_rating")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_rating response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_status")
class AddStatusResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_status request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_status')
        entry_object_id = dump_request_payload("on_status", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_status")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_status response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_support")
class AddSupportResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_support request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_support')
        entry_object_id = dump_request_payload("on_support", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_support")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_support response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_track")
class AddTrackResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_track request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_track')
        entry_object_id = dump_request_payload("on_track", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_track")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_track response {resp}!")
        return resp


@ondc_network_namespace.route("/v1/on_update")
class AddUpdateResponse(Resource):

    @validate_auth_header
    def post(self):
        request_payload = request.get_json()
        log(f"Got the on_update request payload {request_payload} \n headers: {dict(request.headers)}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'on_update')
        entry_object_id = dump_request_payload("on_update", request_payload)
        if resp is None:
            resp = add_bpp_response(request_payload, request_type="on_update")
        update_dumped_request_with_response(entry_object_id, resp)
        log(f"Got the on_update response {resp}!")
        return resp
