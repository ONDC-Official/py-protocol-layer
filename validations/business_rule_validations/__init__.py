from config import get_config_by_name
from validations.business_rule_validations.logistics import validate_logistics_business_rules
from validations.business_rule_validations.retail import validate_retail_business_rules


def validate_business_rules(payload, request_type):
    if get_config_by_name("TYPE").split("_")[0] == "RETAIL":
        return validate_retail_business_rules(payload, request_type)
    else:
        return validate_logistics_business_rules(payload, request_type)
