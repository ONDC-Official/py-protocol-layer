import os

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler

from main import create_app
from main.cron.search_by_city import make_search_operation_along_with_incremental

app = create_app(os.getenv("ENV") or "dev")
scheduler = APScheduler()


if __name__ == "__main__":
    if os.getenv("ENV") is not None:
        scheduler.add_job(id='Search Request for Full Catalog', func=make_search_operation_along_with_incremental,
                          trigger=CronTrigger.from_crontab("30 19 * * *"))
        scheduler.start()
        app.run(host="0.0.0.0", port=app.config["PORT"])
