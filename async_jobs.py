from main import rq


@rq.job("client_forward", timeout=60 * 60 * 24, ttl=60 * 60 * 24 * 7)
def forward_request_to_client(**kwargs):
    from utils.webhook_utils import make_request_to_client
    payload = kwargs["payload"]
    return make_request_to_client(payload["context"]["action"], payload["context"]["core_version"], payload)
