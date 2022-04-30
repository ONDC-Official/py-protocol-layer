import enum
import os
import traceback
from datetime import datetime

from main.controller.user_controller import store_user_with_explicit_password
from main.logger.custom_logging import log


class Status(enum.Enum):
    joined = 1
    invited = 2


def create_admin(email,
                 first_name,
                 last_name,
                 identity_type,
                 company_name,
                 phone_number,
                 role):
    try:
        from main.controller.user_controller import store_user_for_user_info
        now = datetime.now()
        store_user_with_explicit_password(
            **{"email": email, "first_name": first_name, "last_name": last_name, "identity_type": identity_type,
               "company_name": company_name,
               "phone_number": phone_number,
               "role": role,
               "password": os.getenv("SYS_ADMIN_PASSWORD"),
               'created_at': now,
               "last_login_time": now,
               "status": "invited",
               "status_updated_time": now,
               "weekly_report_status": False,
               "is_fairmatic_app_enabled": False,
               })
        log(f"admin created for email {email}")
    except Exception as e:
        traceback.print_exc()
        log("unable to crete admin")


def create_admin_with_dummy_user():
    create_admin("navdeep+admin@dataorc.in", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("pradeep+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("manjunath+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("raghu+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("mohit+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("ethan+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("cynthia+admin@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    create_admin("jt@fairmatic.com", "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
    pass


def create_admin_with_email(email,secret):
    if secret == os.getenv("admin_secret"):
        create_admin(email, "system", "admin", "human", "fairmatic", "911911911", "sys_admin")
        return {"message": "admin_created"}
    else:
        return {"message": "wrong secret"}


def create_beacon_admin_user(email,
                             first_name,
                             last_name,
                             password,
                             company_name,
                             identity_type="human",
                             phone_number=None,
                             role="beacon_admin"):
    now = datetime.now()
    store_user_with_explicit_password(
        **{"email": email, "first_name": first_name, "last_name": last_name, "identity_type": identity_type,
           "company_name": company_name,
           "phone_number": phone_number,
           "role": role,
           "password": password,
           'created_at': now,
           "last_login_time": now,
           "status": "invited",
           "status_updated_time": now,
           "weekly_report_status": False,
           "is_fairmatic_app_enabled": False,
           })



if __name__ == '__main__':
    create_admin_with_dummy_user()
