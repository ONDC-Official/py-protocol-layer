import os

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler

from main import create_app
from main.cron.search_by_city import make_full_catalog_search_requests, make_incremental_catalog_search_requests

app = create_app(os.getenv("ENV") or "dev")
scheduler = APScheduler()


if __name__ == "__main__":
    if os.getenv("ENV") is not None:
        scheduler.add_job(id='Search Request for Full Catalog', func=make_full_catalog_search_requests,
                          trigger=CronTrigger.from_crontab("30 19 * * *"))
        scheduler.add_job(id='Search Request for Incremental Catalog', func=make_incremental_catalog_search_requests,
                          trigger=CronTrigger.from_crontab("0 20 * * *"))
        scheduler.start()
        app.run(host="0.0.0.0", port=app.config["PORT"])
