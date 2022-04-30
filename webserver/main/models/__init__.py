import json
import os

from flask import request, g

from main.create_users import create_admin_with_dummy_user, create_beacon_admin_user
from main.models.kafka import setup_kafka_producer
from main.models.models import Role
from main.service.roles import get_role_types
from ..utils.function_decorators import handle_sql_error


class JsonObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


from .rdb import db

@handle_sql_error
def initialize_role():
    roles = [Role(name=role) for role in get_role_types()]
    db.session.add_all(roles)
    db.session.commit()


def initialize_before_calls(app):
    @app.before_request
    def set_page(page=1):
        page = int(request.args.get('page', 1))
        g.page = page


def run_custom_functions():
    create_beacon_admin_user("mohit+read_only_admin@fairmatic.com",
                                     "mohit","read-only-admin","readonlyadmin42",
                                     "fairmatic")


def init_app(
        app,
        is_init_db: bool = True,
        is_init_kafka: bool = False,
        is_re_init_db: bool = False,
        is_create_admin_logins: bool = False
):
    if is_init_db:
        db.init_app(app)
        initialize_before_calls(app)
        if is_re_init_db:
            db.drop_all()
            db.create_all()
            initialize_role()
        if is_create_admin_logins:
            create_admin_with_dummy_user()
        if os.getenv("enabled_custom_scripts","False") == "True":
            run_custom_functions()
    if is_init_kafka:
        setup_kafka_producer(app)





