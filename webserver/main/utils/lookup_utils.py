import os

from main.config import get_config_by_name
from main.models.subscriber import SubscriberType
from main.utils.cryptic_utils import get_filter_dictionary_or_operation, format_registry_request
from main.utils.webhook_utils import lookup_call


def fetch_subscriber_url_from_lookup(request_type, subscriber_id=None):
    subscriber_type = SubscriberType.BG.name if request_type == 'search' else SubscriberType.BPP.name
    payload = {"type": subscriber_type, "country": get_config_by_name('COUNTRY_CODE'),
               "domain": get_config_by_name('DOMAIN')}
    payload.update({"subscriber_id": subscriber_id}) if subscriber_id else None
    updated_payload = format_registry_request(payload) if os.getenv("ENV") == "pre_prod" else payload
    response, status_code = lookup_call(f"{get_config_by_name('REGISTRY_BASE_URL')}/vlookup",
                                        payload=updated_payload)
    if status_code == 200:
        if response[0].get('network_participant'):
            return response[0].get('network_participant')[0]['subscriber_url']
        else:
            return response[0]['subscriber_url']
    else:
        return None


def get_bpp_public_key_from_header(auth_header):
    header_parts = get_filter_dictionary_or_operation(auth_header.replace("Signature ", ""))
    subscriber_type = SubscriberType.BPP.name
    payload = {"type": subscriber_type, "domain": get_config_by_name('DOMAIN'),
               "subscriber_id": header_parts['keyId'].split("|")[0]}
    response, status_code = lookup_call(f"{get_config_by_name('REGISTRY_BASE_URL')}/lookup", payload=payload)
    if status_code == 200:
        return response[0]['signing_public_key']
    else:
        return None