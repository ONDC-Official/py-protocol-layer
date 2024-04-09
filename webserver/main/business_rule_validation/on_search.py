from datetime import datetime

from main.config import get_config_by_name
from main.models import get_mongo_collection
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response
from main.repository.mongo import collection_find_one


def validate_business_rules_for_full_on_search(payload):
    error = validate_search_request_validity(payload)
    if error:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error}), 400


def validate_business_rules_for_incr_on_search(payload):
    return None


def validate_search_request_validity(payload):
    if get_config_by_name("IS_TEST"):
        return None
    context = payload["context"]
    collection = get_mongo_collection("request_dump")
    filter_criteria = {"action": "search", "request.context.domain": context["domain"],
                       "request.context.transaction_id": context["transaction_id"]}
    search_request = collection_find_one(collection, filter_criteria, keep_created_at=True)
    if search_request:
        minutes_diff = (datetime.utcnow() - search_request['created_at']).total_seconds() // 60
        if minutes_diff < 30:
            return None
    return "No search request was made with given domain and transaction_id in last 30 minutes!"
