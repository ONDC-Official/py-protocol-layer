from flask import g
from funcy import merge

from main import jwt
from main.config import get_config_value_for_name
from main.controller.fleet_controller import get_fleet_info_for_application_id
from main.controller.user_controller import get_user_for_userid
from main.controller.insurance_controller import get_insurance_carrier_name
from main.controller.utils import password_hash
from main.logger.custom_logging import log
from main.service.configuration_service import get_enabled_feature_flags_for_application_id_formatted
from main.utils.encryption import encrypt_objects


def get_additional_flags_based_on_session_type(session_type):
    if session_type == "admin_approval":
        log("session type is admin_approval")
        return {"roles": ["sys_admin"]}
    if session_type == "shadow":
        log("session type is shadow")
        response = get_fleet_info_for_application_id(g.application_id)
        flags_enabled = list(map(lambda x: x["feature_flag_name"],
                                 get_enabled_feature_flags_for_application_id_formatted(
                                     **{"application_id": g.application_id})))
        insurance_carrier_name = get_insurance_carrier_name(g.application_id)
        return {"roles": [g.role], "application_id": response.zendrive_application_id,
                "company_name": response.fleet_name, "api_key": response.api_key, "sdk_key": response.sdk_key,
                "subaccount_id": response.subaccount_id, "is_fairmatic_app_enabled": response.is_fairmatic_app_enabled,
                "distance_unit": response.distance_unit, "flags_enabled": flags_enabled,
                "insurance_carrier_name": insurance_carrier_name}
    return {}


# this will and should be called after previous authentication
def construct_additional_flags_based_on_session_type():
    if hasattr(g, "session"):
        return merge({"purpose": g.session}, get_additional_flags_based_on_session_type(g.session))
    else:
        return {"purpose": "login"}


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    # need to consider the scenario where user might not be present
    user = get_user_for_userid(identity)
    fleet = get_fleet_info_for_application_id(user.application_id)
    insurance_carrier_name = get_insurance_carrier_name(user.application_id)
    flags_enabled = list(map(lambda x: x["feature_flag_name"],get_enabled_feature_flags_for_application_id_formatted(**{"application_id": user.application_id})))
    if user is not None:
        return merge({
            "email": user.email,
            "purpose": user.last_login_time,
            "phone_number": user.phone_number,
            "roles": [role.name for role in get_user_for_userid(identity).roles],
            "company_name": user.company_name,
            "application_id": user.application_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "api_key": getattr(fleet, "api_key", None),
            "subaccount_id": getattr(fleet, "subaccount_id", None),
            "sdk_key": getattr(fleet, "sdk_key", None),
            "domain": get_config_value_for_name("DOMAIN"),
            "is_fairmatic_app_enabled": getattr(fleet, "is_fairmatic_app_enabled", None),
            "distance_unit": getattr(fleet, "distance_unit", 'miles'),
            "flags_enabled": flags_enabled,
            "tracking_id": password_hash(user.email),
            "insurance_carrier_name": insurance_carrier_name,

        }, construct_additional_flags_based_on_session_type())
    else:
        return {}
