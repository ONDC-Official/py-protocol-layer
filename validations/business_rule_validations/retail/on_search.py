from datetime import datetime

from config import get_config_by_name
from models import get_mongo_collection
from utils.mongo_utils import collection_find_one
from validations.business_rule_validations.retail.city_to_pin_code_mappings import get_city_to_pin_codes_mapping

from models.error import BaseError
from utils.ack_utils import get_ack_response


def validate_business_rules_for_full_on_search(payload):
    fn_list = [validate_city_code_with_pin_code_in_locations, validate_search_request_validity]
    for fn in fn_list:
        error = fn(payload)
        if error:
            return get_ack_response(context=payload["context"], ack=False,
                                    error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                           "message": error})
    return None


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


def validate_city_code_with_pin_code_in_locations(payload):
    sheet_link = "https://docs.google.com/spreadsheets/d/12A_B-nDtvxyFh_FWDfp85ss2qpb65kZ7"
    city_code = payload["context"]["city"]
    providers = payload["message"]["catalog"]["bpp/providers"]
    area_codes = []
    for p in providers:
        locations = p["locations"]
        area_codes.extend([lo["address"]["area_code"] for lo in locations])

    city_pin_codes = get_city_to_pin_codes_mapping().get(city_code.split(":")[-1], [])

    are_pin_codes_for_given_city = all(element in city_pin_codes for element in area_codes)
    if not are_pin_codes_for_given_city:
        return f"Provided pin-codes {area_codes} (in location.address) are not from city {city_code}, check {sheet_link}"
    else:
        return None
