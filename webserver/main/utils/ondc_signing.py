# """
# const sodium = _sodium;
#     const digest = sodium.crypto_generichash(64, sodium.from_string(message));
#     const digest_base64 = sodium.to_base64(digest, _sodium.base64_variants.ORIGINAL);
#
#     const signing_string =
#         `(created): ${created}
# (expires): ${expires}
# digest: BLAKE-512=${digest_base64}`
#
#     return { signing_string, created, expires };
# """
# import base64
# import datetime
# import os
#
# import nacl.encoding
# import nacl.hash
# import json
# import ed25519
#
# from nacl.public import PrivateKey
# from nacl.signing import SigningKey
#
#
# def hash_message(msg: str):
#     HASHER = nacl.hash.blake2b
#     digest = HASHER(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
#     digest_str = digest.decode("utf-8")
#     print(f"digest for the string is {digest_str}")
#     return digest_str
#
#
# def create_signing_string(digest_base64, created=None, expires=None):
#     if created == None:
#         created = int(datetime.datetime.now().timestamp())
#     if expires == None:
#         expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
#     signing_string = f"""(created): {created}
# (expires): {expires}
# digest:
# BLAKE-512={digest_base64}
# """
#     return signing_string
#
#
# def sign_response(json_response, created=1641287875, expires=1641291475):
#     signing_key = create_signing_string(hash_message(json.dumps(json_response)), created=created, expires=expires)
#     signer = ed25519.SigningKey(base64.b64decode(os.getenv("private_signing_key")))
#     # See https://github.com/warner/python-ed25519#readme for how the conversion
#     signature = signer.sign(signing_key).signature
#     ######################################################
#     b64signature = base64.b64encode(signature).decode()
#     return b64signature, created, expires
#
#
# if __name__ == '__main__':
#     # hash_message('{"context":{"domain":"nic2004:60212","country":"IND","city":"Kochi","action":"search","core_version":"0.9.1","bap_id":"bap.stayhalo.in","bap_uri":"https://8f9f-49-207-209-131.ngrok.io/protocol/","transaction_id":"e6d9f908-1d26-4ff3-a6d1-3af3d3721054","message_id":"a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d","timestamp":"2022-01-04T09:17:55.971Z","ttl":"P1M"},"message":{"intent":{"fulfillment":{"start":{"location":{"gps":"10.108768, 76.347517"}},"end":{"location":{"gps":"10.102997, 76.353480"}}}}}}')
#     # request_body = {"context": {"domain": "nic2004:60212", "country": "IND", "city": "Kochi", "action": "search",
#     #                             "core_version": "0.9.1", "bap_id": "bap.stayhalo.in",
#     #                             "bap_uri": "https://8f9f-49-207-209-131.ngrok.io/protocol/",
#     #                             "transaction_id": "e6d9f908-1d26-4ff3-a6d1-3af3d3721054",
#     #                             "message_id": "a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d",
#     #                             "timestamp": "2022-01-04T09:17:55.971Z", "ttl": "P1M"}, "message": {"intent": {
#     #     "fulfillment": {"start": {"location": {"gps": "10.108768, 76.347517"}},
#     #                     "end": {"location": {"gps": "10.102997, 76.353480"}}}}}}
#     # os.environ[
#     #     "private_signing_key"] = "lP3sHA+9gileOkXYJXh4Jg8tK0gEEMbf9yCPnFpbldhrAY+NErqL9WD+Vav7TE5tyVXGXBle9ONZi2W7o144eQ=="
#     # sign_response(request_body)
#     signer = SigningKey(
#         base64.b64decode("lP3sHA+9gileOkXYJXh4Jg8tK0gEEMbf9yCPnFpbldhrAY+NErqL9WD+Vav7TE5tyVXGXBle9ONZi2W7o144eQ==".encode('utf-8')))
#     signing_key = """(created): 1641287875
# (expires): 1641291475
# digest: BLAKE-512=b6lf6lRgOweajukcvcLsagQ2T60+85kRh/Rd2bdS+TG/5ALebOEgDJfyCrre/1+BMu5nA94o4DT3pTFXuUg7sw=="""
#     signed = signer.sign(bytes(signing_key, encoding='utf8'), encoding="base64")
#     print(base64.b64encode(signed))
