import os

from main import create_app

app = create_app(os.getenv("ENV") or "dev")


if(os.getenv("ENV") == "prod"):
    app.run(host="localhost", port=app.config["PORT"])
