import enum

from main.models.models import IdentityType


class Roles(enum.Enum):
    sys_admin = 0
    administrator = 1
    fleet_manager = 2
    claim_adjuster = 3
    customer_support = 4
    beacon_admin = 5


def get_role_types():
    return [e.name for e in Roles]


def get_fleet_administrator_roles():
    return [Roles.administrator.name,Roles.sys_admin.name,Roles.fleet_manager.name]


def get_identity_types():
    return [e.name for e in IdentityType]