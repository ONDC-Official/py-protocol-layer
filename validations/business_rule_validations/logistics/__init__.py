from validations.business_rule_validations.logistics.on_status import validate_business_rules_for_on_status


def validate_logistics_business_rules(payload, request_type):
    business_rule_fn = request_type_to_fun_mapping.get(request_type, print)
    return business_rule_fn(payload)


request_type_to_fun_mapping = {
    "on_status": validate_business_rules_for_on_status
}