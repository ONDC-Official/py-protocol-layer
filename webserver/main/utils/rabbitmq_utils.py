import functools
import threading
import time

import pika
from concurrent.futures import ThreadPoolExecutor

from main.config import get_config_by_name
from main.logger.custom_logging import log, log_error


def open_connection_and_channel_if_not_already_open(old_connection, old_channel):
    if old_connection and old_connection.is_open:
        log("Getting old connection and channel")
        return old_connection, old_channel
    else:
        log("Getting new connection and channel")
        rabbitmq_host = get_config_by_name('RABBITMQ_HOST')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        return connection, channel


def open_connection():
    rabbitmq_host = get_config_by_name('RABBITMQ_HOST')
    print(rabbitmq_host)
    return pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))


def close_connection(connection):
    connection.close()


def create_channel(connection):
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    return channel


def declare_queue(channel, queue_name):
    # channel.exchange_declare("test-x", exchange_type="x-delayed-message", arguments={"x-delayed-type": "direct"})
    channel.queue_declare(queue=queue_name)
    # channel.queue_bind(queue=queue_name, exchange="test-x", routing_key=queue_name)


# @retry(3, errors=StreamLostError)
def publish_message_to_queue(channel, exchange, routing_key, body, properties=None):
    log(f"Publishing message of {body}")
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties)


def consume_message(connection, channel, queue_name, consume_fn):

    def do_work(delivery_tag, body):
        thread_id = threading.get_ident()
        log(f'Thread id: {thread_id} Delivery tag: {delivery_tag} Message body: {body}')

        try:
            consume_fn(body)
        except Exception as e:
            log_error(f"Error processing message {body}: {e}")

    def on_message(ch, method_frame, header_frame, body):
        delivery_tag = method_frame.delivery_tag
        executor.submit(do_work, delivery_tag, body)

    executor = ThreadPoolExecutor(max_workers=get_config_by_name('CONSUMER_MAX_WORKERS', 10))
    on_message_callback = functools.partial(on_message)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=True)
    log('Waiting for messages:')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    # Wait for all threads to complete
    executor.shutdown()
    connection.close()
