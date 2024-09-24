from funcy import get_in

from models import get_mongo_collection
from models.error import BaseError
from utils.ack_utils import get_ack_response
from utils.mongo_utils import collection_find_one
from validations.business_rule_validations.retail.common import validate_sum_of_quote_breakup


def validate_business_rules_for_on_status(payload):
    error = validate_authorisation_in_fulfillment(payload)
    if error:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error})


def get_authorisation_objects(fullfillments, start_or_end = "start"):
    authorisation_objects = []
    for f in fullfillments:
        authz = get_in(f, [start_or_end, "authorization"])
        authorisation_objects.append(authz) if authz else None
        return authorisation_objects


def compare_authz_objects(auth1_objects, auth2_objects):
    if len(auth1_objects) != len(auth2_objects):
        return False

    for a1, a2 in zip(auth1_objects, auth2_objects):
        if a1 != a2:
            return False

    return True


def validate_authorisation_in_fulfillment(payload):
    context = payload["context"]
    collection = get_mongo_collection("request_dump")
    filter_criteria = {"action": "update", "request.context.domain": context["domain"],
                       "request.context.transaction_id": context["transaction_id"]}
    update_request = collection_find_one(collection, filter_criteria, keep_created_at=True)
    if update_request:
        update_fulfillments = get_in(update_request, ["request", "message", "order", "fulfillments"], [])
        update_start_authz_objects = get_authorisation_objects(update_fulfillments, "start")
        update_end_authz_objects = get_authorisation_objects(update_fulfillments, "end")

        on_status_fulfillments = get_in(payload, ["message", "order", "fulfillments"], [])
        on_status_start_authz_objects = get_authorisation_objects(on_status_fulfillments, "start")
        on_status_end_authz_objects = get_authorisation_objects(on_status_fulfillments, "end")

        if compare_authz_objects(update_start_authz_objects, on_status_start_authz_objects) \
                and compare_authz_objects(update_end_authz_objects, on_status_end_authz_objects):
            return None
        else:
            return "No search request was made with given domain and transaction_id in last 30 minutes!"
    else:
        return None
