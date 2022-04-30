from datetime import datetime

from cachetools import cached, TTLCache
from flask import g
from flask_jwt_extended import create_access_token, get_jwt
from flask_restplus import abort
from funcy import project, select_values

import main.controller.user_controller as user_controller
from main.config import get_config_value_for_name
from main.controller.fleet_controller import create_fleet
from main.controller.user_controller import get_user_for_userid, store_user_for_user_info, update_personal_details, \
    get_user_for_registration_id_and_password, get_user_by_phone_number_registration_id
from main.models.models import Status
from main.service.configuration_service import check_if_flag_is_enabled_for_application_id
from main.service.roles import Roles, get_role_types
from main.service.xtract_service import create_xtract_user_with_user_model, delete_user_from_xtract
from main.utils.dictionary_utils import get_non_null_values
from main.utils.email_helper import send_password_link_via_email, send_admin_approval_via_email, EmailTypes, \
    send_welcome_link_via_email
from main.utils.function_decorators import check_if_necessary_arguments_present
from main.utils.url import create_link_for_forgot_password, create_link_for_admin_approval


def format_user_response(user_response):
    roles = user_response.pop("roles", None)
    if roles is not None and len(roles) >= 1:
        user_response["role"] = roles[0].get("name", None)
    return user_response


@cached(TTLCache(maxsize=1024, ttl=600))
def get_user_for_id(email):
    return get_user_for_userid(email)


@check_if_necessary_arguments_present(["email", "password"])
def check_user_with_username_password(**kwargs):
    try:
        user = get_user_for_userid(kwargs["email"])
        return user.compare_password(kwargs["password"])
    except:
        return False


@check_if_necessary_arguments_present(["email", "password"])
def check_user_with_regsitration_id_and_password(**kwargs):
    # user should be already be present
    response = get_user_for_registration_id_and_password(kwargs["user_id"], kwargs["password"])
    return response != None


def get_authentication_method_based_on_role(role=None, input_parameters={}):
    # if role == Roles.administrator.name:
    #     return check_user_with_username_password
    # elif role == Roles.fleet_manager.name:
    #     if "type" in input_parameters and input_parameters.get("type") == 'registration_id_based':
    #         return check_user_with_regsitration_id_and_password
    return check_user_with_username_password


def get_user_based_on_authentication_type(authentication_type, **kwargs):
    if authentication_type == check_user_with_regsitration_id_and_password:
        abort(401, "current authorization type not supported")
    elif authentication_type == check_user_with_username_password:
        return get_user_for_userid(kwargs["email"])


def login_with_args(**kwargs):
    authentication_method = get_authentication_method_based_on_role(kwargs["role"], get_non_null_values(kwargs))
    if authentication_method(**kwargs):
        user = get_user_based_on_authentication_type(authentication_method, **kwargs)
        g.session = "login"
        response = create_access_token(identity=user.email)
        # user_controller.update_last_login(user.email)
        return response


def format_args_based_on_role(**kwargs):
    if kwargs["role"] == Roles.administrator.name:
        kwargs.update({"admin_validated": False})
    if kwargs["role"] in get_role_types():
        if kwargs["email"] == None:
            abort(400)
        kwargs.update({"user_id": kwargs["email"]})
        return kwargs
    elif kwargs["role"] == Roles.user.name:
        kwargs.update({"user_id": kwargs["phone_number"]})
        return kwargs


def get_application_id(**kwargs):
    if kwargs.get('application_id', None) is not None:
        return kwargs['application_id']
    try:
        if get_jwt().get('application_id') is not None:
            return get_jwt().get("application_id")
    except:
        # this is in scenario of signups
        pass
    # this is the scenario where user is added inactively
    return None


def create_user(**kwargs):
    kwargs = format_args_based_on_role(**kwargs)
    now = datetime.now()
    kwargs['created_at'] = now
    # default values, this is will be coming from kwargs or need to be fetched from jwt
    kwargs["application_id"] = get_application_id(**kwargs)
    kwargs["last_login_time"] = now
    kwargs["status"] = Status.invited
    kwargs["status_updated_time"] = now
    kwargs["created_at"] = now
    kwargs["is_fairmatic_app_enabled"] = False
    created_user = store_user_for_user_info(**kwargs)
    if check_if_flag_is_enabled_for_application_id(kwargs["application_id"], "fnol"):
        create_xtract_user_with_user_model(created_user)
    return format_user_response(created_user.to_dict())


def create_user_with_password_link_sent(**kwargs):
    if user_controller.check_if_deleted_user_exists(kwargs["email"], get_application_id(**kwargs)):
        kwargs["status"] = Status.invited
        response = update_member_details(**kwargs)
    else:
        response = create_user(**kwargs)
    send_password_link(**{"user_id": kwargs["email"], 'origin': kwargs.get('origin', None)})
    return response


def create_user_if_not_exist(**kwargs):
    if not get_user_for_userid(**project(kwargs, ["user_id"])):
        return create_user(**kwargs)
    return True


def update_member_details(**kwargs):
    user_id = kwargs["email"]
    application_id = get_jwt().get('application_id')
    kwargs['updated_at'] = datetime.now()
    updates = select_values(lambda x: x != None, kwargs)
    new_role = kwargs.get("role")
    old_user = get_user_for_userid(user_id).to_dict()
    user = update_personal_details(user_id, application_id, updates)
    user_dict = user.to_dict()
    if new_role == "fleet_manager" and old_user.get("roles")[0]["name"] != "fleet_manager":
        create_xtract_user_with_user_model(user)
    elif new_role != "fleet_manager" and old_user.get("roles")[0]["name"] == "fleet_manager":
        delete_user_from_xtract(**{"user_id": user_id})
    if user:
        return format_user_response(user_dict)
    abort(400, message="User not found!")


def reset_password(**kwargs):
    user_id = get_jwt()["email"]
    password = kwargs.pop("password")
    user = get_user_by_phone_number_registration_id(user_id)
    if user is not None:
        user_controller.reset_password(user, password)
        return {'message': 'password successfully updated'}
    else:
        return {'error': "Please enter valid Registration ID/Phone number"}


def send_password_link(**kwargs):
    user_id = kwargs.get("user_id")
    origin = kwargs.get("origin", None)
    link = create_link_for_forgot_password(user_id, origin)
    send_password_link_via_email(link, user_id, EmailTypes.password_reset)
    return {"message": "if user is on-boarded, registered email will receive email."}


def send_welcome_link(**kwargs):
    user_id = kwargs.get("user_id")
    link = create_link_for_forgot_password(user_id)
    send_welcome_link_via_email(link, user_id, EmailTypes.password_reset)
    return {"message": "if user is on-boarded, registered email will receive email."}


def create_fleet_and_create_user_to_adduser(**kwargs):
    application_id = create_fleet({"fleet_name": kwargs['company_name'], "phone_number": kwargs["phone_number"]},
                                  do_transaction=False)
    kwargs.update({"application_id": application_id})
    user = create_user(**kwargs).to_dict()
    return user


def send_email_for_admin_approval(**kwargs):
    # create endpoint for_admin_approval
    link = create_link_for_admin_approval(kwargs['email'])
    send_admin_approval_via_email(link, get_config_value_for_name("sign_up_approvers"), EmailTypes.admin_approval,
                                  kwargs)


def create_inactive_administrator_and_send_email_for_admin_approval(**kwargs):
    # create_inactive_user
    create_user(**kwargs)
    send_email_for_admin_approval(**kwargs)


def enable_user_and_create_fleet():
    claims = get_jwt()
    if claims['purpose'] == "admin_approval":
        user = get_user_for_userid(claims["email"])
        if user is not None:
            user.admin_validated = True
            zendrive_application_id = create_fleet({"fleet_name": user.company_name, "phone_number": user.phone_number})
            user.application_id = zendrive_application_id
            user_controller.commit_user_modification(user)
            send_welcome_link(**{"user_id": claims["email"]})
            return {"message": "User has been sent the password reset link"}
        else:
            return {"message": "User not found"}


def get_all_members(**kwargs):
    application_id = get_jwt()['application_id']
    members = user_controller.get_all_members_for_application_id(application_id)
    return [format_user_response(member.to_dict()) for member in members]


def get_shadow_token(**kwargs):
    g.application_id = kwargs["application_id"]
    g.purpose = 'shadow'
    g.session = 'shadow'
    g.role = kwargs['role']
    return create_access_token(get_jwt()['email'])


def delete_user(**kwargs):
    user = user_controller.update_status(kwargs['user_id'], Status.deleted)
    delete_user_from_xtract(**kwargs)
    return user.to_dict()
