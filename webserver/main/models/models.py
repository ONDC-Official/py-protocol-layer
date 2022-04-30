import enum
from dataclasses import dataclass
from flask_login import UserMixin
from main.utils.string_utils import get_encrypted_string, compare_password, compare_file_md5
from sqlalchemy import PrimaryKeyConstraint, Enum
from sqlalchemy_serializer import SerializerMixin

from main.models.rdb import Base
from .rdb import db


class IdentityType(enum.Enum):
    api_key = 1
    sdk_key = 2
    human = 3


class Status(enum.Enum):
    joined = 1
    invited = 2
    deleted = 3


class FeatureFlagType(enum.Enum):
    boolean = 1
    dropdown = 2
    text = 3
    radio = 4


class ScanCode(enum.Enum):
    SCAN0B = "SCAN0B"
    SCAN1B = "SCAN1B"
    SCAN2B_END_1B = "SCAN2B_END_1B"
    SCAN2B_ETC = "SCAN2B_ETC"
    SCAN3B_1B = "SCAN3B_1B"
    SCAN3B_ETC = "SCAN3B_ETC"
    SCAN_USER_ERR = "SCAN_USER_ERR"


@dataclass
class User(Base, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('email'),
    )

    serialize_types = ((enum.Enum, lambda x: x.name),)
    serialize_rules = ('-password_hash','-password_md5_hash')
    email = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String(250))
    password_md5_hash = db.Column(db.String)
    identity_type = db.Column(Enum(IdentityType), nullable=False)
    last_login_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(Enum(Status), nullable=False)
    status_updated_time = db.Column(db.DateTime)
    weekly_report_status = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary='user_roles')
    company_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    #TODO  keeping this as nullale because dump contains null
    phone_number = db.Column(db.String, nullable=True)
    application_id = db.Column(db.String, db.ForeignKey('fleet.zendrive_application_id'),nullable=True)
    admin_validated = db.Column(db.Boolean,nullable=True,default=True)
    downloadable_reports = db.Column(db.Boolean,nullable=True,default=False)

    @property
    def id(self):
        return self.phone_number

    def store_password(self, password):
        self.password_hash = get_encrypted_string(password).decode('utf8')

    def compare_password(self, current_string):
        if self.password_hash != None:
            return compare_password(self.password_hash, current_string)
        else:
            is_matching = compare_file_md5(self.password_md5_hash,current_string)
            if is_matching:
                self.store_password(current_string)
            return is_matching

    def get_user_id(self):
        return self.email

# Define the Role data-model
class Role(Base, SerializerMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(Base, SerializerMixin):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, db.ForeignKey('users.email', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))


class Dummy(Base, SerializerMixin):
    __tablename__ = "test_table"
    column1 = db.Column(db.Integer, primary_key=True)
    column2 = db.Column(db.Integer)
