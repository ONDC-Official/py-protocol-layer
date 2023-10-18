from flask import request
from flask_restx import Namespace, Resource
from main.service.common import bpp_post_call, dump_request_payload, update_dumped_request_with_response
from main.service.search import gateway_search
from main.utils.validation import validate_payload_schema_based_on_version

client_namespace = Namespace('client', description='Client Namespace')


@client_namespace.route("/search")
class GatewaySearch(Resource):

    def post(self):
        request_payload = request.get_json()
        # validate schema based on context version
        resp = validate_payload_schema_based_on_version(request_payload, 'search')
        if resp is None:
            entry_object_id = dump_request_payload("search", request_payload)
            resp = gateway_search(request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/select")
class AddSelectRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'select')
        if resp is None:
            entry_object_id = dump_request_payload("select", request_payload)
            resp = bpp_post_call('select', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/init")
class AddInitRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'init')
        if resp is None:
            entry_object_id = dump_request_payload("init", request_payload)
            resp = bpp_post_call('init', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/confirm")
class AddConfirmRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'confirm')
        if resp is None:
            entry_object_id = dump_request_payload("confirm", request_payload)
            resp = bpp_post_call('confirm', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/cancel")
class AddCancelRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'cancel')
        if resp is None:
            entry_object_id = dump_request_payload("cancel", request_payload)
            resp = bpp_post_call('cancel', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/issue")
class AddIssueRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'issue')
        if resp is None:
            entry_object_id = dump_request_payload("issue", request_payload)
            resp = bpp_post_call('issue', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/issue_status")
class AddIssueStatusRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'issue_status')
        if resp is None:
            entry_object_id = dump_request_payload("issue_status", request_payload)
            resp = bpp_post_call('issue_status', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/rating")
class AddRatingRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'rating')
        if resp is None:
            entry_object_id = dump_request_payload("rating", request_payload)
            resp = bpp_post_call('rating', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/status")
class AddStatusRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'status')
        if resp is None:
            entry_object_id = dump_request_payload("status", request_payload)
            resp = bpp_post_call('status', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/support")
class AddSupportRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'support')
        if resp is None:
            entry_object_id = dump_request_payload("support", request_payload)
            resp = bpp_post_call('support', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/track")
class AddTrackRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'track')
        if resp is None:
            entry_object_id = dump_request_payload("track", request_payload)
            resp = bpp_post_call('track', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp


@client_namespace.route("/update")
class AddUpdateRequest(Resource):

    def post(self):
        request_payload = request.get_json()
        resp = validate_payload_schema_based_on_version(request_payload, 'update')
        if resp is None:
            entry_object_id = dump_request_payload("update", request_payload)
            resp = bpp_post_call('update', request_payload)
            update_dumped_request_with_response(entry_object_id, resp)
            return resp
        else:
            return resp