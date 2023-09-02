import json

from pika.exceptions import AMQPConnectionError
from retry import retry

from main.config import get_config_by_name
from main.logger.custom_logging import log
from main.models import init_database, get_mongo_collection
from main.repository import mongo
from main.service.search import add_search_catalogues, add_incremental_search_catalogues
from main.utils.rabbitmq_utils import create_channel, declare_queue, consume_message, open_connection


def consume_fn(message_string):
    payload = json.loads(message_string)
    log(f"Got the payload {payload}!")

    unique_id = payload["unique_id"]
    collection = get_mongo_collection('on_search_dump')
    on_search_payload = mongo.collection_find_one(collection, {"id": unique_id})
    if on_search_payload:
        on_search_payload.pop("id", None)
        if payload["request_type"] == "full":
            add_search_catalogues(on_search_payload)
        elif payload["request_type"] == "incr":
            add_incremental_search_catalogues(on_search_payload)


@retry(AMQPConnectionError, delay=5, jitter=(1, 3))
def run_consumer():
    init_database()
    queue_name = get_config_by_name('RABBITMQ_QUEUE_NAME')
    connection = open_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    consume_message(connection, channel, queue_name=queue_name,
                    consume_fn=consume_fn)


if __name__ == "__main__":
    run_consumer()
