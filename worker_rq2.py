# rq2_worker
import os

import redis
from rq import Worker

from main import create_app

redis_connection = redis.Redis(host=os.getenv("REDIS_URL", 'localhost'), port=int(os.getenv("REDIS_PORT", 6379)), db=1,
                               password=os.getenv("REDIS_PASSWORD", None))
app = create_app(os.getenv("ENV") or "dev")

# graceful shutdown of db and redis
import atexit


@atexit.register
def shutdown():
    pass
    # shutdown db
    # db.session.remove()
    # print("DB shutdown")
    # shutdown redis
    # redis_connection.close()
    # print("Redis shutdown")
    # close producer


if __name__ == '__main__':
    worker = Worker([os.getenv("QUEUE_NAME", 'client_forward')], connection=redis_connection, default_result_ttl=10,
                    default_worker_ttl=120)
    worker.work()
