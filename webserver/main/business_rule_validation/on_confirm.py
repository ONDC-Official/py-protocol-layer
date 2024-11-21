from main.business_rule_validation.common import validate_sum_of_quote_breakup, validate_item_ids_in_list_and_breakup, \
    validate_request_and_callback_breakup_items, validate_buyer_finder_fee
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response


def validate_business_rules_for_on_confirm(payload):
    fn_list = [validate_sum_of_quote_breakup, validate_item_ids_in_list_and_breakup,
               validate_request_and_callback_breakup_items, validate_buyer_finder_fee]
    for fn in fn_list:
        error = fn(payload)
        if error:
            return get_ack_response(context=payload["context"], ack=False,
                                    error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                           "message": error}), 400
    return None
