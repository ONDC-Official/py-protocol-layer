from config import get_config_by_name
from logger.custom_logging import log
from utils.ack_utils import get_ack_response
from utils.cryptic_utils import create_authorisation_header
from utils.lookup_utils import fetch_subscriber_url_from_lookup
from utils.webhook_utils import post_on_bg_or_bpp


def forward_request(payload, headers):
    action = payload["context"]["action"]
    return forwarding_rules[get_config_by_name("TYPE", "RETAIL_BAP")][action](payload, headers)


def forward_request_to_client_async(payload, _):
    from async_jobs import forward_request_to_client
    kwargs = {"payload": payload}
    forward_request_to_client.queue(**kwargs, timeout=180, queue="request_forward", result_ttl=0)
    return get_ack_response(payload["context"], ack=True), 200


def gateway_search(search_request, headers={}):
    request_type = 'search'
    gateway_url = fetch_subscriber_url_from_lookup(request_type, domain=search_request['context']['domain'])
    search_url = f"{gateway_url}{request_type}" if gateway_url.endswith("/") else f"{gateway_url}/{request_type}"
    auth_header = create_authorisation_header(search_request)
    log(f"making request to bg with {search_request}")
    headers= {'Authorization': auth_header}
    return post_on_bg_or_bpp(search_url, payload=search_request, headers=headers)


def bpp_request(request_payload, _):
    bpp_url = request_payload['context']['bpp_uri']
    action = request_payload['context']['action']
    auth_header = create_authorisation_header(request_payload)
    log(f"making request to bpp with {request_payload}")
    headers = {'Authorization': auth_header}
    return post_on_bg_or_bpp(f"{bpp_url}/{action}", payload=request_payload, headers=headers)


def bap_request(request_payload, _):
    bpp_url = request_payload['context']['bap_uri']
    auth_header = create_authorisation_header(request_payload)
    log(f"making request to bap with {request_payload}")
    headers = {'Authorization': auth_header}
    return post_on_bg_or_bpp(bpp_url, payload=request_payload, headers=headers)


def publish_message_to_queue_async(request_payload, headers={}):
    from async_jobs import publish_message_to_queue
    kwargs = {"payload": request_payload, "headers": headers}
    publish_message_to_queue.queue(**kwargs, timeout=180, queue="queue_forward", result_ttl=0)
    return get_ack_response(request_payload["context"], ack=True), 200


forwarding_rules = {
    "RETAIL_BAP": {
        "search": gateway_search,
        "select": bpp_request,
        "init": bpp_request,
        "confirm": bpp_request,
        "status": bpp_request,
        "track": bpp_request,
        "cancel": bpp_request,
        "update": bpp_request,
        "rating": bpp_request,
        "support": bpp_request,
        "issue": bpp_request,
        "issue_status": bpp_request,

        "on_search": publish_message_to_queue_async,
        "on_select": forward_request_to_client_async,
        "on_init": forward_request_to_client_async,
        "on_confirm": forward_request_to_client_async,
        "on_status": forward_request_to_client_async,
        "on_track": forward_request_to_client_async,
        "on_cancel": forward_request_to_client_async,
        "on_update": forward_request_to_client_async,
        "on_rating": forward_request_to_client_async,
        "on_support": forward_request_to_client_async,
        "on_issue": forward_request_to_client_async,
        "on_issue_status": forward_request_to_client_async,
    },
    "RETAIL_BPP": {
        "search": forward_request_to_client_async,
        "select": forward_request_to_client_async,
        "init": forward_request_to_client_async,
        "confirm": forward_request_to_client_async,
        "status": forward_request_to_client_async,
        "track": forward_request_to_client_async,
        "cancel": forward_request_to_client_async,
        "update": forward_request_to_client_async,
        "rating": forward_request_to_client_async,
        "support": forward_request_to_client_async,
        "issue": forward_request_to_client_async,
        "issue_status": forward_request_to_client_async,

        "on_search": bap_request,
        "on_select": bap_request,
        "on_init": bap_request,
        "on_confirm": bap_request,
        "on_status": bap_request,
        "on_track": bap_request,
        "on_cancel": bap_request,
        "on_update": bap_request,
        "on_rating": bap_request,
        "on_support": bap_request,
        "on_issue": bap_request,
        "on_issue_status": bap_request,
    },
    "LOGISTICS_BAP": {
        "search": gateway_search,
        "select": bpp_request,
        "init": bpp_request,
        "confirm": bpp_request,
        "status": bpp_request,
        "track": bpp_request,
        "cancel": bpp_request,
        "update": bpp_request,
        "rating": bpp_request,
        "support": bpp_request,
        "issue": bpp_request,
        "issue_status": bpp_request,

        "on_search": forward_request_to_client_async,
        "on_select": forward_request_to_client_async,
        "on_init": forward_request_to_client_async,
        "on_confirm": forward_request_to_client_async,
        "on_status": forward_request_to_client_async,
        "on_track": forward_request_to_client_async,
        "on_cancel": forward_request_to_client_async,
        "on_update": forward_request_to_client_async,
        "on_rating": forward_request_to_client_async,
        "on_support": forward_request_to_client_async,
        "on_issue": forward_request_to_client_async,
        "on_issue_status": forward_request_to_client_async,
    },
    "LOGISTICS_BPP": {
        "search": forward_request_to_client_async,
        "select": forward_request_to_client_async,
        "init": forward_request_to_client_async,
        "confirm": forward_request_to_client_async,
        "status": forward_request_to_client_async,
        "track": forward_request_to_client_async,
        "cancel": forward_request_to_client_async,
        "update": forward_request_to_client_async,
        "rating": forward_request_to_client_async,
        "support": forward_request_to_client_async,
        "issue": forward_request_to_client_async,
        "issue_status": forward_request_to_client_async,

        "on_search": bap_request,
        "on_select": bap_request,
        "on_init": bap_request,
        "on_confirm": bap_request,
        "on_status": bap_request,
        "on_track": bap_request,
        "on_cancel": bap_request,
        "on_update": bap_request,
        "on_rating": bap_request,
        "on_support": bap_request,
        "on_issue": bap_request,
        "on_issue_status": bap_request,
    }
}
