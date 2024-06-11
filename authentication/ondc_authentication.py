import json

from utils.ack_utils import get_ack_response
from utils.cryptic_utils import verify_authorisation_header
from utils.lookup_utils import get_bpp_public_key_from_header


def authenticate_ondc_request(payload_str, headers):
    auth_header = headers.get('Authorization')
    context = json.loads(payload_str).get("context", {})
    domain = context.get("domain")
    if auth_header and verify_authorisation_header(auth_header, payload_str.decode("utf-8"),
                                                   public_key=get_bpp_public_key_from_header(auth_header, domain)):
        return None
    else:
        return get_ack_response(context=context, ack=False, error={
            "code": "10001",
            "message": "Invalid Signature"
        })
