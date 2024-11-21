from retry import retry

from main.config import get_config_by_name
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
        return f"qoute.price.value should be sum of breakup.price.value {total_price} != {breakup_price}"


def validate_item_ids_in_list_and_breakup(payload):
    order = payload["message"]["order"]
    breakup_item_ids = [i["@ondc/org/item_id"] for i in order["quote"]["breakup"] if i["@ondc/org/title_type"] == "item"]
    order_item_ids = [i["id"] for i in order["items"]]

    if set(breakup_item_ids) == set(order_item_ids):
        return None
    else:
        return f"Order items and breakup items should be same! {order_item_ids} != {breakup_item_ids}"


@retry(tries=1, delay=0.5)
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
    splits = callback_payload["context"]["action"].split("on_")
    request_action = splits[1] if len(splits) > 1 else ""
    try:
        request_payload = get_request_payload(callback_payload)
    except Exception as e:
        log_error(e)
        return f"ACK for {request_action} should be received before {callback_payload['context']['action']}!"

    request_order_provider = request_payload["message"]["order"]["provider"].get("id")
    callback_order_provider = callback_payload["message"]["order"]["provider"].get("id")
    request_order_items = [(i["id"], i.get("parent_item_id")) for i in request_payload["message"]["order"]["items"]]
    callback_order_items = [(i["id"], i.get("parent_item_id")) for i in callback_payload["message"]["order"]["items"]]

    if request_order_provider != callback_order_provider:
        return f"Order provider should be same in request and callback: {request_order_provider} != {callback_order_provider}"
    elif set(request_order_items) != set(callback_order_items):
        return f"Order items (id, parent_item_id) should be same in request and callback: {request_order_items} != {callback_order_items}"
    else:
        return None


def validate_buyer_finder_fee(payload):
    order = payload["message"]["order"]
    order_bff_type = order.get("payment", {}).get("@ondc/org/buyer_app_finder_fee_type", "")
    order_bff_amount = order.get("payment", {}).get("@ondc/org/buyer_app_finder_fee_amount", "")
    configured_bff_type = get_config_by_name("BAP_FINDER_FEE_TYPE")
    configured_bff_amount = get_config_by_name("BAP_FINDER_FEE_AMOUNT")
    if order_bff_type != configured_bff_type:
        return f"Order Buyer finder fee type '{order_bff_type}' is different from search finder fee type " \
               f"'{configured_bff_type}'!"
    elif float(order_bff_amount) != float(configured_bff_amount):
        return f"Order Buyer finder fee amount '{order_bff_amount}' is different from search finder fee amount " \
               f"'{configured_bff_amount}'!"
    else:
        return None

