from flask import request
from flask_restx import Namespace, Resource

from main.logger.custom_logging import log
from main.service.common import bpp_post_call, dump_request_payload, update_dumped_request_with_response
from main.service.search import gateway_search
from main.utils.validation import validate_payload_schema_based_on_version
from main.utils.webhook_utils import make_request_to_no_dashboard

client_namespace = Namespace('client', description='Client Namespace')


@client_namespace.route("/search")
class GatewaySearch(Resource):

    def post(self):
        request_payload = request.get_json()
        # validate schema based on context version
        log(f"Got the search request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'search')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("search", request_payload)
            resp = gateway_search(request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the search response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/select")
class AddSelectRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the select request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'select')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("select", request_payload)
            resp = bpp_post_call('select', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the select response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/init")
class AddInitRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the init request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'init')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("init", request_payload)
            resp = bpp_post_call('init', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the init response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/confirm")
class AddConfirmRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the confirm request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'confirm')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("confirm", request_payload)
            resp = bpp_post_call('confirm', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the confirm response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/cancel")
class AddCancelRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the cancel request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'cancel')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("cancel", request_payload)
            resp = bpp_post_call('cancel', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the cancel response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/issue")
class AddIssueRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the issue request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'issue')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("issue", request_payload)
            resp = bpp_post_call('issue', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the issue response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/issue_status")
class AddIssueStatusRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the issue_status request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'issue_status')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("issue_status", request_payload)
            resp = bpp_post_call('issue_status', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the issue_status response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/rating")
class AddRatingRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the rating request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'rating')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("rating", request_payload)
            resp = bpp_post_call('rating', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the rating response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/status")
class AddStatusRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the status request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'status')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("status", request_payload)
            resp = bpp_post_call('status', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the status response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/support")
class AddSupportRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the support request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'support')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("support", request_payload)
            resp = bpp_post_call('support', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the support response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/track")
class AddTrackRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the track request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'track')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("track", request_payload)
            resp = bpp_post_call('track', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the track response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/update")
class AddUpdateRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        log(f"Got the update request payload {request_payload}!")
        resp = validate_payload_schema_based_on_version(request_payload, 'update')
        if resp is None:
            make_request_to_no_dashboard(request_payload)
            entry_object_id = dump_request_payload("update", request_payload)
            resp = bpp_post_call('update', request_payload)
            make_request_to_no_dashboard(resp[0], response=True)
            log(f"Got the update response {resp}!")
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp
