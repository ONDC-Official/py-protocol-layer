from main import rq


@rq.job("request_forward", timeout=60 * 60 * 24, ttl=60 * 60 * 24 * 7)
def forward_request_to_client(**kwargs):
    from utils.webhook_utils import make_request_to_client
    payload = kwargs["payload"]
    return make_request_to_client(payload["context"]["action"], payload)


@rq.job("request_forward", timeout=60 * 60 * 24, ttl=60 * 60 * 24 * 7)
def publish_message_to_queue(**kwargs):
    from services.request_dump import dump_on_search_payload
    from config import get_config_by_name
    from services.rabbitmq_publisher import send_message_to_queue_for_given_request
    request_type = kwargs["headers"].get("X-ONDC-Search-Response", "full")
    doc_id = dump_on_search_payload(kwargs["payload"])
    message = {
        "doc_id": str(doc_id),
        "request_type": request_type,
    }
    send_message_to_queue_for_given_request(message) if get_config_by_name('QUEUE_ENABLE') else None
