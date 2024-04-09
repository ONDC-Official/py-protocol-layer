from main.business_rule_validation.common import validate_sum_of_quote_breakup
from main.models.error import BaseError
from main.repository.ack_response import get_ack_response


def validate_business_rules_for_on_cancel(payload):
    error = validate_sum_of_quote_breakup(payload)
    if error:
        return get_ack_response(context=payload["context"], ack=False,
                                error={"type": BaseError.JSON_SCHEMA_ERROR.value, "code": "20000",
                                       "message": error}), 400
