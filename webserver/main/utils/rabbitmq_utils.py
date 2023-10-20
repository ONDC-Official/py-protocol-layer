import functools
import json
import threading
from threading import Timer


import pika


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
    def callback(ch, delivery_tag, body):
        try:
            channel.basic_ack(delivery_tag)
            log(f"Ack message {body} !")
        except:
            log_error(f"Something went wrong for {body} !")

    def do_work(delivery_tag, body):
        thread_id = threading.get_ident()
        log(f'Thread id: {thread_id} Delivery tag: {delivery_tag} Message body: {body}')
        cb = functools.partial(callback, channel, delivery_tag, body)
        # Use a Timer to enforce a maximum processing time for each message
        message_timer = Timer(get_config_by_name("MAX_CONSUME_MESSAGE_TIME"), mark_message_as_failed,
                              args=(delivery_tag, body))
        message_timer.start()

        try:
            consume_fn(body)
        except Exception as e:
            log_error(f"Error processing message {body}: {e}")
            mark_message_as_failed(delivery_tag, body)

        message_timer.cancel()  # Cancel the timer as the message processing is completed
        connection.add_callback_threadsafe(cb)

    def mark_message_as_failed(delivery_tag, body):
        # You can implement logic here to handle failed messages
        log_error(f"Marking message as failed: {body}")
        channel.basic_nack(delivery_tag, requeue=False)

    def on_message(ch, method_frame, header_frame, body):
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target=do_work, args=(delivery_tag, body))
        t.start()
        threads.append(t)

    threads = []
    on_message_callback = functools.partial(on_message)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=False)
    log('Waiting for messages:')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    connection.close()
