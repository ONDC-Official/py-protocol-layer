from models.error import BaseError
from utils.ack_utils import get_ack_response
from validations.business_rule_validations.common import validate_sum_of_quote_breakup


def validate_business_rules_for_on_cancel(payload):
    error = validate_sum_of_quote_breakup(payload)
    if error:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error})
