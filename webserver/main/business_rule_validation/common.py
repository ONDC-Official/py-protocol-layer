from main.logger.custom_logging import log_error
from main.models import get_mongo_collection
from main.repository import mongo


def validate_sum_of_quote_breakup(payload):
    order_quote = payload["message"]["order"]["quote"]
    total_price = float(order_quote["price"]["value"])
    breakup_price = 0
    for p in order_quote["breakup"]:
        breakup_price += float(p["price"]["value"])

    if breakup_price == total_price:
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


def validate_request_and_callback_breakup_item_ids(callback_payload):
    try:
        request_action = callback_payload["context"]["action"].split("on_")[1]
        query = {
            "request.context.action": request_action,
            "request.context.message_id": callback_payload["context"]["message_id"],
            "response.message.ack.status": "ACK",
        }
        request_dump_collection = get_mongo_collection("request_dump")
        request_payload = mongo.collection_find_one(request_dump_collection, query)["request"]
    except Exception as e:
        log_error(e)
        return f"Couldn't find request for associate callback {callback_payload['context']['action']}!"

    request_order_item_ids = [i["id"] for i in request_payload["message"]["order"]["items"]]
    callback_order_item_ids = [i["id"] for i in callback_payload["message"]["order"]["items"]]

    if set(request_order_item_ids) == set(callback_order_item_ids):
        return None
    else:
        return f"Order items are mismatched between request and callback! {request_order_item_ids} != {callback_order_item_ids}"
