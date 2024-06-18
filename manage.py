import os

from main import create_app

app = create_app(os.getenv("ENV", "dev"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config["PORT"])
