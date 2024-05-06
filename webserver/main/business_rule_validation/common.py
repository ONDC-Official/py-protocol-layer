from retry import retry

from main.logger.custom_logging import log_error
from main.models import get_mongo_collection
from main.repository import mongo


def validate_sum_of_quote_breakup(payload):
    order_quote = payload["message"]["order"]["quote"]
    total_price = float(order_quote["price"]["value"])
    breakup_price = 0
    for p in order_quote["breakup"]:
        breakup_price += float(p["price"]["value"])

    if round(breakup_price, 2) == round(total_price, 2):
        return None
    else:
        return f"Total price and sum of breakup are mismatch! {total_price} != {breakup_price}"


def validate_item_ids_in_list_and_breakup(payload):
    order = payload["message"]["order"]
    breakup_item_ids = [i["@ondc/org/item_id"] for i in order["quote"]["breakup"] if i["@ondc/org/title_type"] == "item"]
    order_item_ids = [i["id"] for i in order["items"]]

    if set(breakup_item_ids) == set(order_item_ids):
        return None
    else:
        return f"Order items and breakup items are mismatched! {order_item_ids} != {breakup_item_ids}"


@retry(tries=3, delay=1)
def get_request_payload(callback_payload):
    request_action = callback_payload["context"]["action"].split("on_")[1]
    query = {
        "request.context.action": request_action,
        "request.context.message_id": callback_payload["context"]["message_id"],
        "response.message.ack.status": "ACK",
    }
    request_dump_collection = get_mongo_collection("request_dump")
    request_payload = mongo.collection_find_one(request_dump_collection, query)["request"]
    return request_payload


def validate_request_and_callback_breakup_items(callback_payload):
    try:
        request_payload = get_request_payload(callback_payload)
    except Exception as e:
        log_error(e)
        return f"Couldn't find request for associate callback {callback_payload['context']['action']}!"

    request_order_provider = request_payload["message"]["order"]["provider"].get("id")
    callback_order_provider = callback_payload["message"]["order"]["provider"].get("id")
    request_order_items = [(i["id"], i.get("parent_item_id")) for i in request_payload["message"]["order"]["items"]]
    callback_order_items = [(i["id"], i.get("parent_item_id")) for i in callback_payload["message"]["order"]["items"]]

    if request_order_provider != callback_order_provider:
        return f"Order provider is mismatched between request and callback: {request_order_provider} != {callback_order_provider}"
    elif set(request_order_items) != set(callback_order_items):
        return f"Order items (id, parent_item_id) are mismatched between request and callback: {request_order_items} != {callback_order_items}"
    else:
        return None
