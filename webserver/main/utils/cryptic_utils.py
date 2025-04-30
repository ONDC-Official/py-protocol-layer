import base64
import datetime
import os
import re
import uuid

import nacl.encoding
import nacl.hash
import json
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey, VerifyKey

from main.config import get_config_by_name
from main.models.subscriber import subscriber_type_mapping


def hash_message(msg: str):
    hasher = nacl.hash.blake2b
    digest = hasher(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str


def create_signing_string(digest_base64, created=None, expires=None):
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string


def sign_response(signing_key, private_key):
    private_key64 = base64.b64decode(private_key)
    seed = crypto_sign_ed25519_sk_to_seed(private_key64)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature


def verify_response(signature, signing_key, public_key):
    try:
        public_key64 = base64.b64decode(public_key)
        VerifyKey(public_key64).verify(bytes(signing_key, 'utf8'), base64.b64decode(signature))
        return True
    except Exception as e:
        print(f"Signature verification failed ==>>>>", e)
        return False


def get_filter_dictionary_or_operation(filter_string):
    filter_string_list = re.split(',', filter_string)
    filter_string_list = [x.strip(' ') for x in filter_string_list]  # to remove white spaces from list
    filter_dictionary_or_operation = dict()
    for fs in filter_string_list:
        splits = fs.split('=', maxsplit=1)
        key = splits[0].strip()
        value = splits[1].strip()
        filter_dictionary_or_operation[key] = value.replace("\"", "")
    return filter_dictionary_or_operation


def create_authorisation_header(request_body, created=None, expires=None):
    created = int(datetime.datetime.now().timestamp()) if created is None else created
    expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()) if expires is None else expires
    signing_key = create_signing_string(hash_message(json.dumps(request_body, separators=(',', ':'))),
                                        created=created, expires=expires)
    signature = sign_response(signing_key, private_key=get_config_by_name("BAP_PRIVATE_KEY"))

    subscriber_id = get_config_by_name("BAP_ID")
    unique_key_id = get_config_by_name("BAP_UNIQUE_KEY_ID")
    header = f'Signature keyId="{subscriber_id}|{unique_key_id}|ed25519",algorithm="ed25519",created=' \
             f'"{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'
    return header


def verify_authorisation_header(auth_header, request_body_str, public_key=None):
    header_parts = get_filter_dictionary_or_operation(auth_header.replace("Signature ", ""))
    created = int(header_parts['created'])
    expires = int(header_parts['expires'])
    current_timestamp = int(datetime.datetime.now().timestamp())
    if created <= current_timestamp <= expires and public_key:
        signing_key = create_signing_string(hash_message(request_body_str), created=created, expires=expires)
        return verify_response(header_parts['signature'], signing_key, public_key=public_key)
    else:
        return False


def generate_key_pairs():
    signing_key = SigningKey.generate()
    private_key = base64.b64encode(signing_key._signing_key).decode()
    public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
    return private_key, public_key


def sign_registry_request(request):
    req_obj = []
    req_obj.append(request.get('country')) if request.get('country') else None
    req_obj.append(request.get('domain')) if request.get('domain') else None
    req_obj.append(request.get('type')) if request.get('type') else None
    req_obj.append(request.get('city')) if request.get('city') else None
    req_obj.append(request.get('subscriber_id')) if request.get('subscriber_id') else None

    signing_string = "|".join(req_obj)
    return sign_response(signing_string, private_key=get_config_by_name("BAP_PRIVATE_KEY"))


def format_registry_request_for_pre_prod(request, vlookup=False):
    request['type'] = subscriber_type_mapping[request['type']]
    if vlookup:
        signature = sign_registry_request(request)
        return {
            "sender_subscriber_id": get_config_by_name("BAP_ID"),
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z",
            "search_parameters": request,
            "signature": signature
        }
    else:
        return request


if __name__ == '__main__':
    request_body1 = {"context":{"domain":"nic2004:60212","country":"IND","city":"Kochi","action":"search","core_version":"0.9.1","bap_id":"bap.stayhalo.in","bap_uri":"https://8f9f-49-207-209-131.ngrok.io/protocol/","transaction_id":"e6d9f908-1d26-4ff3-a6d1-3af3d3721054","message_id":"a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d","timestamp":"2022-01-04T09:17:55.971Z","ttl":"P1M"},"message":{"intent":{"fulfillment":{"start":{"location":{"gps":"10.108768, 76.347517"}},"end":{"location":{"gps":"10.102997, 76.353480"}}}}}}
    # os.environ["BAP_PRIVATE_KEY"] = "lP3sHA+9gileOkXYJXh4Jg8tK0gEEMbf9yCPnFpbldhrAY+NErqL9WD+Vav7TE5tyVXGXBle9ONZi2W7o144eQ=="
    # os.environ["BAP_PUBLIC_KEY"] = "awGPjRK6i/Vg/lWr+0xObclVxlwZXvTjWYtlu6NeOHk="
    # private_key1, public_key1 = generate_key_pairs()
    # os.environ["BAP_PRIVATE_KEY"] = private_key1
    # os.environ["BAP_PUBLIC_KEY"] = public_key1
    auth_header1 = create_authorisation_header(request_body1)
    print(auth_header1)
    print(verify_authorisation_header(auth_header1, json.dumps(request_body1, separators=(',', ':')), os.getenv("BAP_PUBLIC_KEY")))
