import os

from flask_migrate import Migrate

from main import create_app
from main.models import db


app = create_app(os.getenv("ENV") or "dev")

# migrate = Migrate(app, db)
# DO NOT REMOVE this
from main.jwt_registers import *

# Setup the Trip Metadata APP
trip_metadata_app = app if os.getenv("ENV") in ["trip_metadata_dev", "trip_metadata_prod"] else None

if(os.getenv("ENV") == "dev"):
    # flask_s3.create_all(app)
    app.run(host="localhost", port=app.config["PORT"])
