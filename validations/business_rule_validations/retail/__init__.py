from validations.business_rule_validations.retail.on_confirm import validate_business_rules_for_on_confirm
from validations.business_rule_validations.retail.on_issue import validate_business_rules_for_on_issue
from validations.business_rule_validations.retail.on_search import \
    validate_business_rules_for_full_on_search, validate_business_rules_for_incr_on_search
from validations.business_rule_validations.retail.on_select import validate_business_rules_for_on_select
from validations.business_rule_validations.retail.on_init import validate_business_rules_for_on_init


def validate_retail_business_rules(payload, request_type):
    business_rule_fn = request_type_to_fun_mapping.get(request_type, print)
    return business_rule_fn(payload)


request_type_to_fun_mapping = {
    "full_on_search": validate_business_rules_for_full_on_search,
    "inc_on_search": validate_business_rules_for_incr_on_search,
    "on_select": validate_business_rules_for_on_select,
    "on_init": validate_business_rules_for_on_init,
    "on_confirm": validate_business_rules_for_on_confirm,
    "on_issue": validate_business_rules_for_on_issue,
}