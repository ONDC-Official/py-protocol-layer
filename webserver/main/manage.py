import os

from main import create_app

app = create_app(os.getenv("ENV") or "dev")


if __name__ == "__main__":
    if os.getenv("ENV") is not None:
        # flask_s3.create_all(app)
        app.run(host="0.0.0.0", port=app.config["PORT"])
