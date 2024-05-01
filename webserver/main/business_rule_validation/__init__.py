from main.business_rule_validation.on_confirm import validate_business_rules_for_on_confirm
from main.business_rule_validation.on_search import validate_business_rules_for_full_on_search, \
    validate_business_rules_for_incr_on_search
from main.business_rule_validation.on_select import validate_business_rules_for_on_select
from main.business_rule_validation.on_init import validate_business_rules_for_on_init


def validate_business_rules(payload, request_type):
    business_rule_fn = request_type_to_fun_mapping[request_type]
    return business_rule_fn(payload)


request_type_to_fun_mapping = {
    "full_on_search": validate_business_rules_for_full_on_search,
    "incr_on_search": validate_business_rules_for_incr_on_search,
    "on_select": validate_business_rules_for_on_select,
    "on_init": validate_business_rules_for_on_init,
    "on_confirm": validate_business_rules_for_on_confirm,
}


