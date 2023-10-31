import os

from main.config import get_config_by_name
from main.models.subscriber import SubscriberType
from main.utils.cryptic_utils import get_filter_dictionary_or_operation, format_registry_request_for_pre_prod
from main.utils.webhook_utils import lookup_call


def fetch_subscriber_url_from_lookup(request_type, subscriber_id=None, domain=None):
    subscriber_type = SubscriberType.BG.name if request_type == 'search' else SubscriberType.BPP.name
    payload = {"type": subscriber_type, "country": get_config_by_name('COUNTRY_CODE')}
    payload.update({"domain": domain}) if domain and domain != '*' else None
    payload.update({"subscriber_id": subscriber_id}) if subscriber_id else None
    updated_payload = format_registry_request_for_pre_prod(payload) if os.getenv("ENV") == "pre_prod" else payload
    response, status_code = lookup_call(f"{get_config_by_name('REGISTRY_BASE_URL')}/lookup",
                                        payload=updated_payload)
    if status_code == 200 and len(response) > 0:
        if response[0].get('network_participant'):
            subscriber_id = response[0]['subscriber_id']
            subscriber_url = response[0].get('network_participant')[0]['subscriber_url']
            return f"https://{subscriber_id}{subscriber_url}"
        else:
            return response[0]['subscriber_url']
    else:
        return get_config_by_name('REGISTRY_BASE_URL')


def get_bpp_public_key_from_header(auth_header):
    header_parts = get_filter_dictionary_or_operation(auth_header.replace("Signature ", ""))
    unique_key_id_field = "ukId" if os.getenv("ENV") == "pre_prod" else "unique_key_id"
    payload = {
        "domain": get_config_by_name('DOMAIN'),
        "country": get_config_by_name('COUNTRY_CODE'),
        unique_key_id_field: header_parts['keyId'].split("|")[1]
    }
    response, status_code = lookup_call(f"{get_config_by_name('REGISTRY_BASE_URL')}/lookup",
                                        payload=payload)

    if status_code == 200:
        return response[0]['signing_public_key']
    else:
        return None
