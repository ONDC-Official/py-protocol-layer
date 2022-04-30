from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, MetaData
from sqlalchemy.ext.declarative import declarative_base

# db = SQLAlchemy(session_options={'autocommit': True})
metadata = MetaData()
Base = declarative_base(metadata=metadata)

db = SQLAlchemy(metadata=metadata)
# migrate = Migrate()
# migrate = Migrate(current_app, db)


def initialize_db(recreate=False):
    global db, migrate
    from main.models.models import User, Applications, OTP, Role, UserRoles, UserTaxDetails
    if recreate:
        db.drop_all()
    db.create_all()


def execute_string(sql_string):
    with db.engine.connect() as con:
        rs = con.execute(sql_string)
        for row in rs:
            yield (row)


def execute_string_with_parameters(sql_string, parameteres):
    with db.engine.connect() as con:
        rs = con.execute(text(sql_string), parameteres)
        for row in rs:
            yield (row)
