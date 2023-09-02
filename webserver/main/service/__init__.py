import json
from pika.exceptions import StreamLostError
from retry import retry

from main.config import get_config_by_name
from main.logger.custom_logging import log
from main.utils.rabbitmq_utils import declare_queue, publish_message_to_queue, \
    open_connection_and_channel_if_not_already_open

rabbitmq_connection, rabbitmq_channel = None, None


@retry(StreamLostError, tries=3, delay=1, jitter=(1, 3))
def send_message_to_queue_for_given_request(payload, properties=None):
    global rabbitmq_connection, rabbitmq_channel
    rabbitmq_connection, rabbitmq_channel = open_connection_and_channel_if_not_already_open(rabbitmq_connection,
                                                                                            rabbitmq_channel)
    queue_name = get_config_by_name('RABBITMQ_QUEUE_NAME')
    declare_queue(rabbitmq_channel, queue_name)
    log(f"Sending message with payload : {payload} to {queue_name}")
    publish_message_to_queue(rabbitmq_channel, exchange='', routing_key=queue_name, body=json.dumps(payload),
                             properties=properties)
