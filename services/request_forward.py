from config import get_config_by_name
from logger.custom_logging import log
from services.rabbitmq_publisher import send_message_to_queue_for_given_request
from services.request_dump import dump_on_search_payload
from utils.cryptic_utils import create_authorisation_header
from utils.lookup_utils import fetch_subscriber_url_from_lookup
from utils.webhook_utils import post_on_bg_or_bpp, make_request_to_client


def forward_request(payload, headers):
    forwarding_rules[get_config_by_name("TYPE", "BAP")](payload, headers)


def forward_request_to_client(payload, _):
    make_request_to_client(payload["context"]["action"], payload["context"]["core_version"], payload)


def gateway_search(search_request, headers={}):
    request_type = 'search'
    gateway_url = fetch_subscriber_url_from_lookup(request_type, domain=search_request['context']['domain'])
    search_url = f"{gateway_url}{request_type}" if gateway_url.endswith("/") else f"{gateway_url}/{request_type}"
    auth_header = create_authorisation_header(search_request)
    log(f"making request to bg with {search_request}")
    headers.update({'Authorization': auth_header})
    return post_on_bg_or_bpp(search_url, payload=search_request, headers=headers)


def bpp_request(request_payload, _):
    bpp_url = request_payload['context']['bpp_uri']
    auth_header = create_authorisation_header(request_payload)
    log(f"making request to bpp with {request_payload}")
    headers = {'Authorization': auth_header}
    return post_on_bg_or_bpp(bpp_url, payload=request_payload, headers=headers)


def bap_request(request_payload, _):
    bpp_url = request_payload['context']['bap_uri']
    auth_header = create_authorisation_header(request_payload)
    log(f"making request to bap with {request_payload}")
    headers = {'Authorization': auth_header}
    return post_on_bg_or_bpp(bpp_url, payload=request_payload, headers=headers)


def publish_message_to_queue(request_payload, headers={}):
    request_type = headers.get("X-ONDC-Search-Response", "full")
    doc_id = dump_on_search_payload(request_payload)
    message = {
        "doc_id": str(doc_id),
        "request_type": request_type,
    }
    send_message_to_queue_for_given_request(message) if get_config_by_name('QUEUE_ENABLE') else None


forwarding_rules = {
    "BAP": {
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

        "on_search": publish_message_to_queue,
        "on_select": forward_request_to_client,
        "on_init": forward_request_to_client,
        "on_confirm": forward_request_to_client,
        "on_status": forward_request_to_client,
        "on_track": forward_request_to_client,
        "on_cancel": forward_request_to_client,
        "on_update": forward_request_to_client,
        "on_rating": forward_request_to_client,
        "on_support": forward_request_to_client,
        "on_issue": forward_request_to_client,
        "on_issue_status": forward_request_to_client,
    },
    "BPP": {
        "search": forward_request_to_client,
        "select": forward_request_to_client,
        "init": forward_request_to_client,
        "confirm": forward_request_to_client,
        "status": forward_request_to_client,
        "track": forward_request_to_client,
        "cancel": forward_request_to_client,
        "update": forward_request_to_client,
        "rating": forward_request_to_client,
        "support": forward_request_to_client,
        "issue": forward_request_to_client,
        "issue_status": forward_request_to_client,

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
