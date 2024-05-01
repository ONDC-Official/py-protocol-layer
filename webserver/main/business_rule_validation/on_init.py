from main.business_rule_validation.common import validate_sum_of_quote_breakup, validate_item_ids_in_list_and_breakup, \
    validate_request_and_callback_breakup_item_ids
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response


def validate_business_rules_for_on_init(payload):
    fn_list = [validate_sum_of_quote_breakup, validate_item_ids_in_list_and_breakup,
               validate_request_and_callback_breakup_item_ids, validate_fulfillment_ids]
    for fn in fn_list:
        error = fn(payload)
        if error:
            return get_ack_response(context=payload["context"], ack=False,
                                    error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                           "message": error}), 400
    return None


def validate_fulfillment_ids(payload):
    order = payload["message"]["order"]
    item_fulfillment_ids = set([i["fulfillment_id"] for i in order.get("items", [])])
    fulfillment_ids = set([i["id"] for i in order.get("fulfillments", [])])
    quote_breakup_ids = set()
    for i in order.get("quote", {}).get("breakup", []):
        if i["@ondc/org/title_type"] == "delivery":
            quote_breakup_ids.add(i["@ondc/org/item_id"])

    if item_fulfillment_ids == fulfillment_ids == quote_breakup_ids:
        return None
    else:
        return "Fulfillment ids are not getting correctly mapped!"
