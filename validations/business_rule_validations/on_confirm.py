from models.error import BaseError
from utils.ack_utils import get_ack_response
from validations.business_rule_validations.common import validate_sum_of_quote_breakup, \
    validate_item_ids_in_list_and_breakup, validate_request_and_callback_breakup_items


def validate_business_rules_for_on_confirm(payload):
    fn_list = [validate_sum_of_quote_breakup, validate_item_ids_in_list_and_breakup,
               validate_request_and_callback_breakup_items]
    for fn in fn_list:
        error = fn(payload)
        if error:
            return get_ack_response(context=payload["context"], ack=False,
                                    error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                           "message": error})
    return None
