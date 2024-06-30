from datetime import datetime

from main.business_rule_validation.city_to_pin_code_mappings import get_city_to_pin_codes_mapping
from main.config import get_config_by_name
from main.models import get_mongo_collection
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response
from main.repository.mongo import collection_find_one


def validate_business_rules_for_full_on_search(payload):
    fn_list = [validate_search_request_validity, validate_city_code_with_pin_code_in_locations]
    for fn in fn_list:
        error = fn(payload)
        if error:
            return get_ack_response(context=payload["context"], ack=False,
                                    error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                           "message": error}), 400
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
        minutes_diff = (payload['created_at'] - search_request['created_at']).total_seconds() // 60
        if minutes_diff < 30:
            return None
    return "No search request was made with given domain and transaction_id in last 30 minutes!"


def validate_on_search_provider_is_unique(payload):
    context = payload["context"]
    collection = get_mongo_collection("on_search_dump")
    provider_ids = [p["id"] for p in payload["message"]["catalog"]["bpp/providers"]]
    filter_criteria = {"context.domain": context["domain"],
                       "context.bpp_id": context["bpp_id"],
                       "context.transaction_id": context["transaction_id"],
                       "message.catalog.bpp/providers.id": {"$in": provider_ids}
                       }
    on_search_request = collection_find_one(collection, filter_criteria, keep_created_at=False)
    if on_search_request:
        return f'On search request already found for transaction-id: {context["transaction_id"]} of ' \
               f'{context["bpp_id"]} : {provider_ids}'
    return None


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
