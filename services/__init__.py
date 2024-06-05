from services.request_dump import dump_request_payload, update_dumped_request_with_response
from services.request_forward import forward_request


def request_dump_and_forward(payload, headers):
    entry_object_id = dump_request_payload(payload["context"]["action"], payload)
    resp = forward_request(payload, headers)
    update_dumped_request_with_response(entry_object_id, resp)
