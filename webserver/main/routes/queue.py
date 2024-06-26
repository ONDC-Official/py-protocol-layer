import threading

from flask import request
from flask_restx import Namespace, Resource, reqparse

from main.config import get_config_by_name
from main.cron.search_by_city import make_full_catalog_search_requests, make_incremental_catalog_search_requests, \
    make_search_operation_along_with_incremental
from main.service import send_message_to_queue_for_given_request
from main.utils.decorators import token_required

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

queue_namespace = Namespace('queue', description='Queue Namespace', authorizations=authorizations)


@queue_namespace.route("/queue/push-message-to-queue")
class FullCatalogSearch(Resource):

    def post(self):
        request_payload = request.get_json()
        message = {
            "doc_id": request_payload["doc_id"],
            "request_type": request_payload.get("type", "full"),
        }
        send_message_to_queue_for_given_request(message) if get_config_by_name('QUEUE_ENABLE') else None
        return {"status": "success"}, 200
